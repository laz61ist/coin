"""E2E: TC5in1Strategy'nin tam sinyal zinciri, GERÇEK freqtrade API'siyle.

Review bulgusu: birim testler yalnız gösterge katmanını kilitliyordu; canlıda botu
susturan NaN kapılaması ve strateji-seviyesi lookahead bu testlerin kör noktasıydı.
Bu dosya o boşluğu kapatır: sentetik iki-rejimli seri (düşüş → yükseliş) üzerinde
populate_indicators → entry/exit zinciri uçtan uca koşar.

freqtrade kurulu değilse atlanır (birim testler yine koşar):
  pip install freqtrade && python -m pytest tests/test_e2e_strategy.py -q
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("freqtrade", reason="e2e için freqtrade gerekir")

STRAT_DIR = Path(__file__).resolve().parents[1] / "user_data" / "strategies"
sys.path.insert(0, str(STRAT_DIR))

spec = importlib.util.spec_from_file_location("TC5in1Strategy", STRAT_DIR / "TC5in1Strategy.py")
strat_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(strat_mod)
TC5in1Strategy = strat_mod.TC5in1Strategy

PAIR = "BTC/USDT:USDT"
N = 5000  # gösterge ısınması ~1000 bar; kalan ~4000 bar sinyal alanı


def _make_1h() -> pd.DataFrame:
    t = np.arange(N, dtype=float)
    wiggle = 6.0 * np.sin(2 * np.pi * t / 96)
    down = 250.0 - 0.048 * t
    up = 130.0 + 0.052 * (t - 2500)
    close = np.where(t < 2500, down, up) + wiggle
    rng = np.random.default_rng(42)
    close = close + rng.normal(0, 0.3, N)
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=N, freq="1h", tz="UTC"),
            "open": np.roll(close, 1),
            "high": close * 1.004,
            "low": close * 0.996,
            "close": close,
            "volume": 100.0,
        }
    )
    df.loc[0, "open"] = close[0]
    return df


def _make_4h(df_1h: pd.DataFrame) -> pd.DataFrame:
    g = df_1h.set_index("date").resample("4h")
    df = pd.DataFrame(
        {
            "open": g["open"].first(),
            "high": g["high"].max(),
            "low": g["low"].min(),
            "close": g["close"].last(),
            "volume": g["volume"].sum(),
        }
    ).reset_index()
    return df


class _StubDP:
    """Testte DataProvider yerine geçer: yalnız 4h informative beslemesi."""

    def __init__(self, df_4h: pd.DataFrame):
        self._df_4h = df_4h

    def get_pair_dataframe(self, pair: str, timeframe: str) -> pd.DataFrame:
        assert timeframe == "4h"
        return self._df_4h.copy()

    def current_whitelist(self):
        return [PAIR]


def _run_chain(df_1h: pd.DataFrame) -> pd.DataFrame:
    strat = TC5in1Strategy({"stake_currency": "USDT", "trading_mode": "futures", "runmode": "backtest"})
    strat.dp = _StubDP(_make_4h(df_1h))
    meta = {"pair": PAIR}
    df = strat.populate_indicators(df_1h.copy(), meta)
    df = strat.populate_entry_trend(df, meta)
    df = strat.populate_exit_trend(df, meta)
    return df


@pytest.fixture(scope="module")
def chain():
    return _run_chain(_make_1h())


def test_warmup_columns_filled_at_tail(chain):
    tail = chain.iloc[-500:]
    for col in ("pmax_dir", "mavw", "nw_upper", "nw_lower", "ema200_4h"):
        assert tail[col].notna().all(), f"{col} kuyrukta NaN — canlıda bot susar"


def test_signals_fire_in_both_regimes(chain):
    longs = chain["enter_long"].fillna(0).sum()
    shorts = chain["enter_short"].fillna(0).sum()
    assert longs >= 1, "yükseliş rejiminde tek long girişi bile yok — zincir kopuk"
    assert shorts >= 1, "düşüş rejiminde tek short girişi bile yok — zincir kopuk"
    # rejim filtresi: long girişleri EMA üstünde, short girişleri altında olmalı
    le = chain[chain["enter_long"] == 1]
    se = chain[chain["enter_short"] == 1]
    assert (le["close"] > le["ema200_4h"]).all()
    assert (se["close"] < se["ema200_4h"]).all()


def test_entry_mask_matches_documented_logic(chain):
    ema = chain["ema200_4h"]
    flip_up = (chain["pmax_dir"] == 1) & (chain["pmax_dir"].shift(1) == -1)
    expected = (
        (chain["close"] > ema)
        & flip_up
        & chain["mavw_rising"]
        & (chain["close"] < chain["nw_upper"])
        & (chain["volume"] > 0)
    )
    actual = chain["enter_long"].fillna(0) == 1
    pd.testing.assert_series_equal(actual, expected.fillna(False), check_names=False)


def test_exit_is_pmax_flip(chain):
    flip_down = (chain["pmax_dir"] == -1) & (chain["pmax_dir"].shift(1) == 1)
    actual = chain["exit_long"].fillna(0) == 1
    pd.testing.assert_series_equal(actual, flip_down.fillna(False), check_names=False)


def test_leverage_is_capped_at_two():
    """F5 risk sözleşmesi: kaldıraç tavanı — regresyonu likidasyon riski demek."""
    strat = TC5in1Strategy({"stake_currency": "USDT", "trading_mode": "futures"})
    common = dict(pair=PAIR, current_time=None, current_rate=100.0,
                  proposed_leverage=5.0, entry_tag=None, side="long")
    assert strat.leverage(max_leverage=10.0, **common) == 2.0
    assert strat.leverage(max_leverage=1.5, **common) == 1.5  # borsa limiti düşükse ona uy


def test_protections_shape_contract():
    """Koruma katmanı bildirimseldir — yazım hatası sessizce devre dışı bırakır."""
    strat = TC5in1Strategy({"stake_currency": "USDT", "trading_mode": "futures"})
    prots = strat.protections
    methods = {p["method"] for p in prots}
    assert methods == {"CooldownPeriod", "MaxDrawdown", "StoplossGuard"}
    dd = next(p for p in prots if p["method"] == "MaxDrawdown")
    assert dd["max_allowed_drawdown"] <= 0.20  # docs/03 kill-switch sözleşmesi


def test_shadow_hook_logs_but_always_allows(monkeypatch, tmp_path):
    """LLM shadow köprüsü: girişi ASLA engellemez, ama açıkken görüşü loglar."""
    import importlib
    import llm_advisor.advisor as adv
    importlib.reload(adv)
    log = tmp_path / "veto.jsonl"
    monkeypatch.setattr(adv, "LOG_DIR", tmp_path)
    monkeypatch.setenv("TC_LLM_SHADOW", "true")
    monkeypatch.setenv("TC_LLM_MOCK", "true")  # ağsız
    strat = TC5in1Strategy({"stake_currency": "USDT", "trading_mode": "futures"})
    import datetime as _dt
    ok = strat.confirm_trade_entry(
        pair=PAIR, order_type="limit", amount=1.0, rate=100.0,
        time_in_force="gtc", current_time=_dt.datetime(2026, 7, 24), entry_tag=None, side="long",
    )
    assert ok is True                       # emir HER ZAMAN onaylanır (shadow)
    assert (tmp_path / "veto_log.jsonl").exists()  # görüş loglandı

    # kapalıyken (varsayılan) hiç LLM çağrısı yok, yine izin verir
    monkeypatch.delenv("TC_LLM_SHADOW", raising=False)
    assert strat.confirm_trade_entry(
        pair=PAIR, order_type="limit", amount=1.0, rate=100.0,
        time_in_force="gtc", current_time=_dt.datetime(2026, 7, 24), entry_tag=None, side="short",
    ) is True


def test_no_lookahead_at_strategy_level():
    """Strateji-seviyesi repaint sözleşmesi: seri kısaltılınca geçmiş sinyaller değişmez.

    Not: son ~2 bar, kısaltılmış koşuda henüz kapanmamış 4h mumunun merge hizası
    yüzünden farklılaşabilir — freqtrade canlıda da son barı yeniden hesaplar;
    sözleşme 'kapanmış barlar değişmez' der, onu test ediyoruz.
    """
    full_df = _make_1h()
    full = _run_chain(full_df)
    cut = _run_chain(full_df.iloc[:4200].reset_index(drop=True))
    stable = 4200 - 8  # son 2 adet 4h mumu payı
    for col in ("enter_long", "enter_short", "exit_long", "exit_short"):
        a = full[col].fillna(0).iloc[:stable].reset_index(drop=True)
        b = cut[col].fillna(0).iloc[:stable].reset_index(drop=True)
        pd.testing.assert_series_equal(a, b, check_names=False), col
