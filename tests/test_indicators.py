"""F1 birim testleri — sentetik seriyle davranış doğrulama.

Tam kabul (H1) TradingView karşılaştırması ister (docs/03 §1); buradaki testler
mantık/repaint sözleşmesini kilitler: pytest tests/ -q
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_MOD = Path(__file__).resolve().parents[1] / "user_data" / "strategies" / "tc_indicators.py"
spec = importlib.util.spec_from_file_location("tc_indicators", _MOD)
tc = importlib.util.module_from_spec(spec)
sys.modules["tc_indicators"] = tc
spec.loader.exec_module(tc)


def _ohlc(closes: np.ndarray) -> pd.DataFrame:
    c = pd.Series(closes, dtype=float)
    return pd.DataFrame(
        {"open": c.shift(1).fillna(c), "high": c * 1.005, "low": c * 0.995, "close": c}
    )


@pytest.fixture
def trend_up():
    return _ohlc(np.linspace(100, 200, 600))


@pytest.fixture
def trend_down():
    return _ohlc(np.linspace(200, 100, 600))


def test_wma_matches_manual():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    # WMA(3) son değeri: (3*1 + 4*2 + 5*3) / 6
    assert tc.wma(s, 3).iloc[-1] == pytest.approx((3 + 8 + 15) / 6)


def test_mavilim_rises_in_uptrend(trend_up):
    m = tc.mavilim(trend_up["close"])
    tail = m.dropna().tail(50)
    assert (tail.diff().dropna() > 0).all()


def test_pmax_direction_follows_regime(trend_up, trend_down):
    up = tc.pmax(trend_up)
    down = tc.pmax(trend_down)
    assert (up["pmax_dir"].tail(100) == 1).all()
    assert (down["pmax_dir"].tail(100) == -1).all()
    # PMax çizgisi long rejimde fiyatın altında kalmalı
    valid = up.dropna().tail(100)
    assert (valid["pmax"] < trend_up["close"].tail(100).to_numpy()).all()


def test_pmax_no_lookahead(trend_up):
    """Repaint sözleşmesi: t anındaki değer, t sonrası veri değişince değişmemeli."""
    full = tc.pmax(trend_up)
    cut = tc.pmax(trend_up.iloc[:400])
    pd.testing.assert_series_equal(
        full["pmax_dir"].iloc[:400], cut["pmax_dir"], check_names=False
    )


def test_nw_envelope_no_lookahead(trend_up):
    full = tc.nw_envelope(trend_up["close"], window=100)
    cut = tc.nw_envelope(trend_up["close"].iloc[:400], window=100)
    pd.testing.assert_series_equal(
        full["nw_mid"].iloc[:400], cut["nw_mid"], check_names=False
    )


def test_nw_bands_contain_mid(trend_up):
    nw = tc.nw_envelope(trend_up["close"], window=100).dropna()
    assert (nw["nw_upper"] >= nw["nw_mid"]).all()
    assert (nw["nw_lower"] <= nw["nw_mid"]).all()


def test_linreg_endpoint_tracks_trend(trend_up):
    lr = tc.linreg_channel(trend_up["close"], length=50).dropna()
    # Düz çizgide endpoint fiyata çok yakın olmalı
    err = (lr["lr_mid"] - trend_up["close"].loc[lr.index]).abs().max()
    assert err < 1.0
