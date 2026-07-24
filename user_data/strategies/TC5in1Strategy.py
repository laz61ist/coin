"""TC5in1 confluence stratejisi — docs/04 §6 iskeletinin freqtrade uygulaması.

Karar zinciri (docs/03 §2 mimarisi):
  rejim filtresi = 4h EMA200  →  tetik = PMax yön dönüşü  →
  teyit = Mavilim eğimi       →  veto = NW zarf ucunda aşırı uzama

F2 kabulü: bu parametreler walk-forward'dan geçmeden optimize edilmiş sayılmaz.
"""

import logging
import os
from datetime import datetime

from freqtrade.strategy import IStrategy, merge_informative_pair
from pandas import DataFrame

from tc_indicators import mavilim, nw_envelope, pmax

logger = logging.getLogger(__name__)


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
    # Isınma bütçesi: NW zarf zinciri 2×500-1 = 999 bar ister; 4h EMA200'ün
    # ağırlık açığının ihmal edilebilir olması ~600 adet 4h barı = 2400 saat ister.
    # 900 ile bot canlıda NaN yüzünden hiç sinyal üretmiyordu (review bulgusu).
    startup_candle_count = 2500

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
        # min_periods: veri yetersizse sessizce sapmış EMA yerine görünür NaN üret
        informative["ema200"] = informative["close"].ewm(
            span=200, adjust=False, min_periods=200
        ).mean()
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

        # NaN bekçisi: kritik kolon son barda NaN ise giriş koşulları sessizce
        # False'a düşer ve bot "işlem yok" görünür — bunu görünür hataya çevir.
        critical = ["pmax_dir", "mavw", "nw_upper", f"ema200_{self.informative_timeframe}"]
        nan_cols = [c for c in critical if dataframe[c].isna().iloc[-1]]
        if nan_cols:
            logger.warning(
                "%s: son barda NaN kolonlar %s — startup_candle_count/veri geçmişi yetersiz, "
                "bu barda sinyal üretilemez",
                metadata["pair"], nan_cols,
            )

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

    def confirm_trade_entry(
        self, pair, order_type, amount, rate, time_in_force,
        current_time, entry_tag, side, **kwargs,
    ) -> bool:
        """SHADOW köprüsü: giriş anında LLM görüşünü LOGLAR ama emri ASLA engellemez.

        TC_LLM_SHADOW=true iken llm_advisor.run_veto çağrılır; çıktı jsonl'a yazılır,
        dönüş her zaman True'dur (emir yetkisi yok — docs/03 §2 + kaynakça §5).
        Kapalıysa (varsayılan) veya hata olursa sessizce izin ver — bot durmasın.
        """
        if os.getenv("TC_LLM_SHADOW", "").lower() in ("1", "true", "yes"):
            try:
                import sys as _sys
                _root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                if _root not in _sys.path:
                    _sys.path.insert(0, _root)
                from llm_advisor.advisor import run_veto

                run_veto(
                    signal={"pair": pair, "side": side, "time": str(current_time),
                            "indicators": {"rate": float(rate)}},
                    headlines=[],  # haber kaynağı entegrasyonu sonraki adım
                    mock=os.getenv("TC_LLM_MOCK", "").lower() in ("1", "true", "yes"),
                )
            except Exception as exc:  # shadow katman botu ASLA düşürmez
                logger.warning("shadow veto atlandı (%s): %s", pair, exc)
        return True  # emir yetkisi YOK — giriş her zaman onaylanır
