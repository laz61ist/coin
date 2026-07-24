#!/usr/bin/env python3
"""Walk-forward backtest orkestratörü + parametre hassasiyet taraması (F2).

Neden: tek dönemlik backtest overfit üretir (kaynakça §4, Gort ve ark. dersi).
Bu araç stratejiyi kaydırmalı train/test pencerelerinde koşturur; eğitim-pencere
kârı test penceresinde çöküyorsa bunu raporda açıkça gösterir.

v1 kapsamı: SABİT parametreli rolling değerlendirme (pencere başına hyperopt yok —
o F2b'dir). Parametreler TC_* ortam değişkenleriyle değiştirilebilir; hassasiyet
modu bunu kullanır.

Kullanım (önce scripts/download_data.sh):
  python3 scripts/walk_forward.py                      # walk-forward, docker ile
  python3 scripts/walk_forward.py --runner local       # lokal freqtrade kuruluysa
  python3 scripts/walk_forward.py --mode sensitivity   # PMax parametre ızgarası
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import statistics
import subprocess
import sys
import zipfile

REPO = pathlib.Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO / "user_data" / "backtest_results"
REPORTS_DIR = REPO / "reports"
CONFIG_IN_CONTAINER = "/freqtrade/user_data/config.futures.json"
CONFIG_LOCAL = str(REPO / "user_data" / "config.futures.json")
STRATEGY = "TC5in1Strategy"

# Rapor kabul eşikleri (başlangıç değerleri — docs/03 F2; walk-forward sonuçlarına
# göre gözden geçirilebilir ama raporda hangi eşiğin kullanıldığı hep yazılır)
MIN_POSITIVE_WINDOW_RATIO = 0.5
MAX_WINDOW_DRAWDOWN = 0.20


# ---------- pencere matematiği (saf, test edilebilir) ----------

def month_start(d: dt.date) -> dt.date:
    return d.replace(day=1)


def add_months(d: dt.date, months: int) -> dt.date:
    y, m = divmod((d.year * 12 + d.month - 1) + months, 12)
    return dt.date(y, m + 1, 1)


def timerange(a: dt.date, b: dt.date) -> str:
    return f"{a:%Y%m%d}-{b:%Y%m%d}"


def build_windows(
    start: dt.date, end: dt.date, train_months: int = 6, test_months: int = 2
) -> list[dict]:
    """Kaydırmalı pencereler: [train_start, train_end) + [train_end, test_end).

    Stride = test_months (test pencereleri bitişik, çakışmasız). Son pencere
    `end`i aşarsa üretilmez — kısmi test penceresi yanıltıcı olur.
    """
    windows = []
    train_start = month_start(start)
    while True:
        train_end = add_months(train_start, train_months)
        test_end = add_months(train_end, test_months)
        if test_end > end:
            break
        windows.append(
            {
                "train": timerange(train_start, train_end),
                "test": timerange(train_end, test_end),
            }
        )
        train_start = add_months(train_start, test_months)
    return windows


# ---------- freqtrade koşucu ----------

def backtest_cmd(runner: str, trange: str, env_overrides: dict[str, str]) -> list[str]:
    if runner == "docker":
        cmd = ["docker", "compose", "run", "--rm"]
        for k, v in env_overrides.items():
            cmd += ["-e", f"{k}={v}"]
        cmd += [
            "freqtrade", "backtesting",
            "--config", CONFIG_IN_CONTAINER,
            "--strategy", STRATEGY,
            "--timerange", trange,
            "--export", "trades",
        ]
        return cmd
    return [
        "freqtrade", "backtesting",
        "--config", CONFIG_LOCAL,
        "--strategy", STRATEGY,
        "--timerange", trange,
        "--export", "trades",
    ]


def run_backtest(runner: str, trange: str, env_overrides: dict[str, str] | None = None) -> dict:
    env_overrides = env_overrides or {}
    cmd = backtest_cmd(runner, trange, env_overrides)
    env = None
    if runner == "local":
        env = {**os.environ, **env_overrides}
    print(f"[wf] backtest {trange} {env_overrides or ''}", flush=True)
    proc = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"backtest başarısız ({trange}):\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
        )
    return load_last_result()


# ---------- sonuç ayrıştırma (defansif: alan yoksa None, uydurma yok) ----------

def load_last_result(results_dir: pathlib.Path = RESULTS_DIR) -> dict:
    pointer = results_dir / ".last_result.json"
    latest = json.loads(pointer.read_text())["latest_backtest"]
    path = results_dir / latest
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            inner = [n for n in zf.namelist() if n.endswith(".json") and "config" not in n]
            # aynı kök adlı ana json'u tercih et
            main = next((n for n in inner if pathlib.Path(n).stem == path.stem), inner[0])
            data = json.loads(zf.read(main))
    else:
        data = json.loads(path.read_text())
    return data


def extract_metrics(data: dict, strategy: str = STRATEGY) -> dict:
    s = data.get("strategy", {}).get(strategy, {})

    def g(*keys):
        for k in keys:
            if s.get(k) is not None:
                return s[k]
        return None

    total = g("total_trades", "trades")
    wins = s.get("wins")
    return {
        "profit_total": g("profit_total"),          # oran (0.05 = %5)
        "profit_factor": g("profit_factor"),
        "max_drawdown": g("max_drawdown_account", "max_drawdown"),
        "sharpe": g("sharpe"),
        "sortino": g("sortino"),
        "trades": total,
        "winrate": (wins / total) if (wins is not None and total) else g("winrate"),
        "market_change": g("market_change"),
    }


# ---------- rapor ----------

def _pct(x) -> str:
    return "—" if x is None else f"{x * 100:.1f}%"


def _num(x) -> str:
    return "—" if x is None else f"{x:.2f}"


def render_walkforward_report(rows: list[dict], out_path: pathlib.Path) -> str:
    test_profits = [r["test"]["profit_total"] for r in rows if r["test"]["profit_total"] is not None]
    positive = sum(1 for p in test_profits if p > 0)
    ratio = positive / len(test_profits) if test_profits else 0.0
    worst_dd = max(
        (r["test"]["max_drawdown"] for r in rows if r["test"]["max_drawdown"] is not None),
        default=None,
    )
    verdict_pass = (
        bool(test_profits)
        and ratio >= MIN_POSITIVE_WINDOW_RATIO
        and (worst_dd is None or worst_dd <= MAX_WINDOW_DRAWDOWN)
    )

    lines = [
        "# Walk-Forward Raporu — TC5in1Strategy",
        "",
        f"Pencere: train 6 ay / test 2 ay, kaydırma 2 ay. Eşikler: pozitif test penceresi ≥ {MIN_POSITIVE_WINDOW_RATIO:.0%}, pencere MDD ≤ {MAX_WINDOW_DRAWDOWN:.0%}.",
        "",
        "| # | Train | Test | Train kâr | Test kâr | Test MDD | PF | Sharpe | İşlem | Piyasa | Bozulma |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(rows, 1):
        tr, te = r["train"], r["test"]
        degraded = (
            "⚠️"
            if tr["profit_total"] is not None
            and te["profit_total"] is not None
            and tr["profit_total"] > 0 > te["profit_total"]
            else ""
        )
        lines.append(
            f"| {i} | {r['train_range']} | {r['test_range']} | {_pct(tr['profit_total'])} "
            f"| {_pct(te['profit_total'])} | {_pct(te['max_drawdown'])} | {_num(te['profit_factor'])} "
            f"| {_num(te['sharpe'])} | {te['trades'] or 0} | {_pct(te['market_change'])} | {degraded} |"
        )

    lines += [
        "",
        "## Özet",
        f"- Pozitif test penceresi: {positive}/{len(test_profits)} ({ratio:.0%})",
        f"- Medyan test kârı: {_pct(statistics.median(test_profits)) if test_profits else '—'}",
        f"- En kötü pencere MDD: {_pct(worst_dd)}",
        f"- **Sonuç: {'GEÇTİ ✅' if verdict_pass else 'KALDI ❌'}** (eşikler yukarıda; H2/F2 kabulü için ayrıca ≥3 sembol + ≥2 rejim şartı geçerli)",
        "",
        "Not: '⚠️ Bozulma' = train penceresi kârlı, hemen ardından gelen test penceresi zararda — rejim bağımlılığı/overfit işareti (Chun & Lee vakasındaki örüntü, kaynakça §4.4).",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    return "\n".join(lines)


def render_sensitivity_report(grid_rows: list[dict], out_path: pathlib.Path) -> str:
    lines = [
        "# Parametre Hassasiyet Raporu — PMax (TC5in1Strategy)",
        "",
        "Amaç: kâr tek bir parametre kombinasyonuna mı sıkışmış (cliff) yoksa komşularda da mı yaşıyor? Cliff = overfit işareti (Gort ve ark. dersi).",
        "",
        "| ATR uzunluğu | Çarpan | Kâr | MDD | İşlem |",
        "|---|---|---|---|---|",
    ]
    for r in grid_rows:
        m = r["metrics"]
        lines.append(
            f"| {r['atr']} | {r['mult']} | {_pct(m['profit_total'])} | {_pct(m['max_drawdown'])} | {m['trades'] or 0} |"
        )
    profits = [r["metrics"]["profit_total"] for r in grid_rows if r["metrics"]["profit_total"] is not None]
    cliff = bool(profits) and max(profits) > 0 and min(profits) < 0
    lines += [
        "",
        f"**Cliff uyarısı: {'VAR ⚠️ — bazı komşu kombinasyonlar zararda; parametre seçimi kırılgan' if cliff else 'yok — kâr/zarar deseni komşularda tutarlı'}**",
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))
    return "\n".join(lines)


# ---------- ana akış ----------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["walkforward", "sensitivity"], default="walkforward")
    ap.add_argument("--runner", choices=["docker", "local"], default="docker")
    ap.add_argument("--start", default="2021-01-01")
    ap.add_argument("--end", default=dt.date.today().isoformat())
    ap.add_argument("--train-months", type=int, default=6)
    ap.add_argument("--test-months", type=int, default=2)
    args = ap.parse_args()

    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end)

    if args.mode == "walkforward":
        windows = build_windows(start, end, args.train_months, args.test_months)
        if not windows:
            print("HATA: verilen aralık tek pencere bile üretmiyor", file=sys.stderr)
            return 1
        rows = []
        for w in windows:
            rows.append(
                {
                    "train_range": w["train"],
                    "test_range": w["test"],
                    "train": extract_metrics(run_backtest(args.runner, w["train"])),
                    "test": extract_metrics(run_backtest(args.runner, w["test"])),
                }
            )
        out = REPORTS_DIR / f"walk_forward_{dt.date.today():%Y%m%d}.md"
        print(render_walkforward_report(rows, out))
        print(f"\n[wf] rapor: {out}")
        return 0

    # sensitivity: PMax ızgarası, tüm dönem
    full = timerange(start, end)
    grid_rows = []
    for atr_len in (8, 10, 12, 14):
        for mult in (2.0, 2.5, 3.0, 3.5, 4.0):
            env = {"TC_PMAX_ATR": str(atr_len), "TC_PMAX_MULT": str(mult)}
            metrics = extract_metrics(run_backtest(args.runner, full, env))
            grid_rows.append({"atr": atr_len, "mult": mult, "metrics": metrics})
    out = REPORTS_DIR / f"sensitivity_{dt.date.today():%Y%m%d}.md"
    print(render_sensitivity_report(grid_rows, out))
    print(f"\n[wf] rapor: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
