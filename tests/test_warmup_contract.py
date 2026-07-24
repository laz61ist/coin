"""Isınma (startup) sözleşmesi testleri — review bulgusu #2/#3'ün regresyon kilidi.

Bot canlıda startup_candle_count kadar mumla çalışır; NW zarfı 2×window-1 bar,
4h EMA200 ise 200×4 saat ısınma ister. Bu testler bütçe küçültülürse kırılır.
"""

import importlib.util
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

_MOD = ROOT / "user_data" / "strategies" / "tc_indicators.py"
spec = importlib.util.spec_from_file_location("tc_indicators2", _MOD)
tc = importlib.util.module_from_spec(spec)
sys.modules["tc_indicators2"] = tc
spec.loader.exec_module(tc)

NW_WINDOW = 500
NW_WARMUP = 2 * NW_WINDOW - 1          # out: window; mae: +window-1
EMA200_4H_WARMUP_1H = 200 * 4          # min_periods=200 × 4 saat


def _strategy_source() -> str:
    return (ROOT / "user_data" / "strategies" / "TC5in1Strategy.py").read_text()


def test_startup_candle_count_covers_warmup():
    m = re.search(r"startup_candle_count\s*=\s*(\d+)", _strategy_source())
    assert m, "startup_candle_count bulunamadı"
    startup = int(m.group(1))
    assert startup >= NW_WARMUP, f"NW zarfı {NW_WARMUP} bar ister, startup={startup}"
    assert startup >= EMA200_4H_WARMUP_1H, (
        f"4h EMA200 (min_periods=200) {EMA200_4H_WARMUP_1H} saat ister, startup={startup}"
    )


def test_nw_first_valid_bar_matches_budget():
    n = NW_WARMUP + 50
    src = pd.Series(np.linspace(100, 150, n))
    nw = tc.nw_envelope(src, window=NW_WINDOW)
    assert nw["nw_mid"].first_valid_index() == NW_WINDOW - 1
    assert nw["nw_upper"].first_valid_index() == NW_WARMUP - 1
    # bütçe içinde son bar dolu olmalı
    assert not nw["nw_upper"].iloc[-1] != nw["nw_upper"].iloc[-1]  # not NaN


def test_strategy_has_no_unused_linreg():
    # review bulgusu: linreg hesaplanıp kullanılmıyordu — geri gelirse ya kullanılsın
    # ya da import edilmesin
    src = _strategy_source()
    assert "linreg_channel" not in src


def test_dry_run_flag_pinned_in_compose():
    compose = (ROOT / "docker-compose.yml").read_text()
    assert "--dry-run" in compose, "compose'daki --dry-run bayrağı F4 kapısına kadar kalkamaz"


def test_backtest_cache_disabled():
    wf_src = (ROOT / "scripts" / "walk_forward.py").read_text()
    assert wf_src.count('"--cache", "none"') >= 2, "her iki runner'da --cache none şart"
