"""F2 walk-forward orkestratörünün saf (subprocess'siz) parçalarının testleri."""

import datetime as dt
import importlib.util
import sys
from pathlib import Path

_MOD = Path(__file__).resolve().parents[1] / "scripts" / "walk_forward.py"
spec = importlib.util.spec_from_file_location("walk_forward", _MOD)
wf = importlib.util.module_from_spec(spec)
sys.modules["walk_forward"] = wf
spec.loader.exec_module(wf)


def test_build_windows_boundaries():
    windows = wf.build_windows(dt.date(2021, 1, 1), dt.date(2022, 1, 1), 6, 2)
    # 6+2 aylık ilk pencere: train 2021-01→07, test 07→09; stride 2 ay
    assert windows[0] == {"train": "20210101-20210701", "test": "20210701-20210901"}
    assert windows[1]["train"] == "20210301-20210901"
    # hiçbir test penceresi bitişi 2022-01-01'i aşamaz
    for w in windows:
        assert w["test"].split("-")[1] <= "20220101"
    assert len(windows) == 3


def test_build_windows_empty_when_range_too_short():
    assert wf.build_windows(dt.date(2021, 1, 1), dt.date(2021, 6, 1), 6, 2) == []


def test_add_months_year_rollover():
    assert wf.add_months(dt.date(2021, 11, 15), 3) == dt.date(2022, 2, 1)


def test_extract_metrics_defensive():
    data = {
        "strategy": {
            "TC5in1Strategy": {
                "profit_total": 0.12,
                "max_drawdown_account": 0.08,
                "wins": 6,
                "total_trades": 10,
                "market_change": 0.30,
            }
        }
    }
    m = wf.extract_metrics(data)
    assert m["profit_total"] == 0.12
    assert m["max_drawdown"] == 0.08
    assert m["winrate"] == 0.6
    assert m["sharpe"] is None  # alan yok → None, uydurma yok
    assert m["market_change"] == 0.30


def test_extract_metrics_missing_strategy():
    m = wf.extract_metrics({})
    assert all(v is None for v in m.values())


def _row(train_p, test_p, dd=0.05):
    empty = {k: None for k in ("profit_total", "profit_factor", "max_drawdown", "sharpe", "sortino", "trades", "winrate", "market_change")}
    return {
        "train_range": "20210101-20210701",
        "test_range": "20210701-20210901",
        "train": {**empty, "profit_total": train_p},
        "test": {**empty, "profit_total": test_p, "max_drawdown": dd, "trades": 5},
    }


def test_walkforward_report_pass_and_degradation(tmp_path):
    rows = [_row(0.10, 0.05), _row(0.08, -0.02), _row(0.02, 0.04)]
    out = tmp_path / "r.md"
    text = wf.render_walkforward_report(rows, out)
    assert out.exists()
    assert "2/3" in text          # pozitif pencere sayımı
    assert "GEÇTİ" in text        # 2/3 ≥ %50 ve MDD eşik altı
    assert "⚠️" in text           # train + / test - penceresi işaretlendi


def test_walkforward_report_fail_on_drawdown(tmp_path):
    rows = [_row(0.10, 0.05, dd=0.35), _row(0.08, 0.02)]
    text = wf.render_walkforward_report(rows, tmp_path / "r.md")
    assert "KALDI" in text


def test_sensitivity_report_cliff(tmp_path):
    empty = {k: None for k in ("profit_total", "profit_factor", "max_drawdown", "sharpe", "sortino", "trades", "winrate", "market_change")}
    grid = [
        {"atr": 10, "mult": 3.0, "metrics": {**empty, "profit_total": 0.2, "trades": 30}},
        {"atr": 10, "mult": 3.5, "metrics": {**empty, "profit_total": -0.1, "trades": 28}},
    ]
    text = wf.render_sensitivity_report(grid, tmp_path / "s.md")
    assert "VAR ⚠️" in text


def test_backtest_cmd_docker_env_passthrough():
    cmd = wf.backtest_cmd("docker", "20210101-20210301", {"TC_PMAX_MULT": "2.5"})
    assert "docker" == cmd[0]
    assert "-e" in cmd and "TC_PMAX_MULT=2.5" in cmd
    assert "--timerange" in cmd and "20210101-20210301" in cmd
