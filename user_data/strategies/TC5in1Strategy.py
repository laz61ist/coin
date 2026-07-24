"""TC5in1 confluence stratejisi — docs/04 §6 iskeletinin freqtrade uygulaması.

Karar zinciri (docs/03 §2 mimarisi):
  rejim filtresi = 4h EMA200  →  tetik = PMax yön dönüşü  →
  teyit = Mavilim eğimi       →  veto = NW zarf ucunda aşırı uzama

F2 kabulü: bu parametreler walk-forward'dan geçmeden optimize edilmiş sayılmaz.
"""

import os
from datetime import datetime

from freqtrade.strategy import IStrategy, merge_informative_pair
from pandas import DataFrame

from tc_indicators import linreg_channel, mavilim, nw_envelope, pmax


class TC5in1Strategy(IStrategy):
    INTERFACE_VERSION = 3

    # scripts/walk_forward.py --mode sensitivity bu değişkenlerle ızgara tarar
    PMAX_ATR = int(os.getenv("TC_PMAX_ATR", "10"))
    PMAX_MULT = float(os.getenv("TC_PMAX_MULT", "3.0"))
    PMAX_MA_LEN = int(os.getenv("TC_PMAX_MA_LEN", "9"))
    NW_BANDWIDTH = float(os.getenv("TC_NW_BW", "8.0"))

    timeframe = "1h"
    informative_timeframe = "4h"
    can_short = True

    # F2'de walk-forward ile gözden geçirilecek muhafazakâr başlangıçlar
    minimal_roi = {"0": 0.10}
    stoploss = -0.03
    trailing_stop = False
    process_only_new_candles = True
    startup_candle_count = 900  # 4h EMA200 + NW window için yeterli geçmiş

    # Kill-switch katmanı (docs/03 §4 F3 tatbikatı bunların üstüne gelir)
    @property
    def protections(self):
        return [
            {"method": "CooldownPeriod", "stop_duration_candles": 3},
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 336,  # ~2 hafta (1h)
                "trade_limit": 10,
                "stop_duration_candles": 168,
                "max_allowed_drawdown": 0.15,
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 96,
                "trade_limit": 4,
                "stop_duration_candles": 24,
                "only_per_pair": False,
            },
        ]

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        return [(pair, self.informative_timeframe) for pair in pairs]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # --- 4h rejim filtresi (non-repaint: yalnız kapanmış 4h barı) ---
        informative = self.dp.get_pair_dataframe(
            pair=metadata["pair"], timeframe=self.informative_timeframe
        )
        informative["ema200"] = informative["close"].ewm(span=200, adjust=False).mean()
        dataframe = merge_informative_pair(
            dataframe, informative, self.timeframe, self.informative_timeframe, ffill=True
        )

        # --- 1h sinyal katmanı ---
        pm = pmax(
            dataframe,
            atr_length=self.PMAX_ATR,
            multiplier=self.PMAX_MULT,
            ma_length=self.PMAX_MA_LEN,
            ma_type="EMA",
        )
        dataframe["pmax"] = pm["pmax"]
        dataframe["pmax_dir"] = pm["pmax_dir"]

        dataframe["mavw"] = mavilim(dataframe["close"])
        dataframe["mavw_rising"] = dataframe["mavw"] > dataframe["mavw"].shift(1)

        nw = nw_envelope(dataframe["close"], bandwidth=self.NW_BANDWIDTH, window=500, mult=3.0)
        dataframe["nw_upper"] = nw["nw_upper"]
        dataframe["nw_lower"] = nw["nw_lower"]

        lr = linreg_channel(dataframe["close"], length=100, mult=2.0)
        dataframe["lr_mid"] = lr["lr_mid"]

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        ema = dataframe[f"ema200_{self.informative_timeframe}"]
        flip_up = (dataframe["pmax_dir"] == 1) & (dataframe["pmax_dir"].shift(1) == -1)
        flip_down = (dataframe["pmax_dir"] == -1) & (dataframe["pmax_dir"].shift(1) == 1)

        dataframe.loc[
            (dataframe["close"] > ema)
            & flip_up
            & dataframe["mavw_rising"]
            & (dataframe["close"] < dataframe["nw_upper"])
            & (dataframe["volume"] > 0),
            "enter_long",
        ] = 1

        dataframe.loc[
            (dataframe["close"] < ema)
            & flip_down
            & (~dataframe["mavw_rising"])
            & (dataframe["close"] > dataframe["nw_lower"])
            & (dataframe["volume"] > 0),
            "enter_short",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Çıkış: PMax rejimi tersine döner (stoploss/ROI/protections ayrıca devrede)
        dataframe.loc[
            (dataframe["pmax_dir"] == -1) & (dataframe["pmax_dir"].shift(1) == 1),
            "exit_long",
        ] = 1
        dataframe.loc[
            (dataframe["pmax_dir"] == 1) & (dataframe["pmax_dir"].shift(1) == -1),
            "exit_short",
        ] = 1
        return dataframe

    def leverage(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_leverage: float,
        max_leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        # docs/03 §4 F5 risk sözleşmesi: kaldıraç tavanı 3x; başlangıçta 2x sabit
        return min(2.0, max_leverage)
