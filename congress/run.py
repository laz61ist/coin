"""F6 orkestratörü: veri -> sıralama -> hedef -> delta -> (dry-run | paper emir) -> rapor.

Kullanım:
  python3 -m congress.run --data all_transactions.json --prices-json fiyatlar.json          # DRY-RUN (varsayılan)
  python3 -m congress.run --data ... --prices-json ... --approve                             # paper emirleri gönder
  python3 -m congress.run --data ... --prices-json ... --leader-filter data/leaders.txt      # F6b deneyi

Veri: senate-stock-watcher aggregate formatı (raw.githubusercontent.com/timothycarambat/
senate-stock-watcher-data/master/aggregate/all_transactions.json). Fiyat: --prices-json
({ticker: {"YYYY-MM-DD": px}}) ya da kurulu ise yfinance (canlı makinede).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

from congress.mirror import (
    build_target_portfolio, compute_delta, kill_switch_triggered, open_positions,
)
from congress.models import load_trades
from congress.ranking import DEFAULT_ASSUMED_LAG_DAYS, rank_members

REPO = pathlib.Path(__file__).resolve().parents[1]
STATE_PATH = REPO / "data" / "congress_state.json"
REPORT_DIR = REPO / "reports"

LAG_WARNING = (
    "⚠️ ŞERH: STOCK Act işlemlerin açıklanmasına 45 güne kadar izin verir "
    "(pratik medyan ~26 gün). Kopyalanan her pozisyon HAFTALARCA ESKİ bilgiye dayanır; "
    "getiriler bu raporda açıklama-tarihli metodolojiyle hesaplanmıştır. "
    "Literatür genel Kongre kopyalamasında risk-ayarlı alfa bulmuyor (kaynakça §6)."
)


def dict_price_provider(table: dict):
    def provider(ticker: str, date: dt.date):
        series = table.get(ticker) or {}
        key = date.isoformat()
        if key in series:
            return float(series[key])
        # o gün fiyat yoksa geriye doğru en yakın işlem gününü ara (maks 7 gün)
        for i in range(1, 8):
            k = (date - dt.timedelta(days=i)).isoformat()
            if k in series:
                return float(series[k])
        return None
    return provider


def yf_price_provider():
    import yfinance as yf  # canlı makinede: pip install yfinance

    cache: dict[str, object] = {}

    def provider(ticker: str, date: dt.date):
        if ticker not in cache:
            cache[ticker] = yf.download(
                ticker, period="2y", interval="1d", progress=False, auto_adjust=True
            )["Close"]
        series = cache[ticker]
        try:
            window = series.loc[: date.isoformat()]
            return float(window.iloc[-1]) if len(window) else None
        except Exception:
            return None
    return provider


def load_state(path: pathlib.Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"positions": {}, "hwm": 0.0, "last_run": None, "member": None}


def save_state(state: dict, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=1, ensure_ascii=False))


def run_once(
    trades: list[dict], prices, broker, state: dict, asof: dt.date,
    assumed_lag_days: int = DEFAULT_ASSUMED_LAG_DAYS,
    member_filter: set[str] | None = None,
    approve: bool = False,
) -> dict:
    """Tek koşu; rapor sözlüğü döndürür. approve=False -> hiçbir emir gönderilmez."""
    equity = broker.account_equity()
    hwm = max(state.get("hwm", 0.0), equity)

    if kill_switch_triggered(equity, state.get("hwm", 0.0)):
        return {
            "asof": asof.isoformat(), "kill_switch": True, "equity": equity,
            "hwm": state.get("hwm"), "orders": [], "ranking": [],
            "message": "KILL SWITCH: HWM'den -%15 — pozisyonlar kapatılmalı, bot durdu. "
                       "Devam için insan kararı gerekir (docs/03 §4 F3 tatbikatı).",
        }

    ranking = rank_members(
        trades, prices, asof,
        assumed_lag_days=assumed_lag_days, member_filter=member_filter,
    )
    if not ranking:
        return {"asof": asof.isoformat(), "kill_switch": False, "equity": equity,
                "orders": [], "ranking": [], "message": "Sıralanabilir üye yok "
                "(min işlem eşiği veya fiyat verisi yetersiz)."}

    top = ranking[0]["member"]
    positions = open_positions(trades, top, asof, assumed_lag_days)
    target = build_target_portfolio(positions, equity)
    current = state.get("positions", {}) if state.get("member") == top else {}
    orders = compute_delta(target, current)

    if approve and orders:
        for o in orders:
            broker.submit_notional_order(o["ticker"], o["usd"], o["side"])
        state.update({"positions": target, "member": top})
    state["hwm"] = hwm
    state["last_run"] = asof.isoformat()

    return {
        "asof": asof.isoformat(), "kill_switch": False, "equity": equity,
        "member": top, "ranking": ranking[:10], "target": target,
        "orders": orders, "approved": approve,
        "message": "Değişiklik yok." if not orders else f"{len(orders)} delta emri.",
    }


def render_report(result: dict, out_dir: pathlib.Path | None = None) -> pathlib.Path:
    # None -> modül değişkenini ÇAĞRI ANINDA oku (monkeypatch/override çalışsın)
    out_dir = out_dir if out_dir is not None else REPORT_DIR
    lines = [f"# Kongre Kopyalama Raporu — {result['asof']}", "", LAG_WARNING, ""]
    if result.get("kill_switch"):
        lines += [f"## 🛑 {result['message']}", f"- Equity: {result['equity']}",
                  f"- HWM: {result['hwm']}"]
    else:
        lines += [f"Seçilen üye: **{result.get('member', '—')}** | Equity: {result['equity']}", "",
                  "| # | Üye | Skor | Kullanılan alım | Fiyatsız atlanan |", "|---|---|---|---|---|"]
        for i, r in enumerate(result.get("ranking", []), 1):
            lines.append(
                f"| {i} | {r['member']} | {r['score'] * 100:.1f}% | {r['buys_used']} "
                f"| {r['buys_skipped_no_price']} |"
            )
        lines += ["", f"## Emirler — {result['message']}"]
        for o in result.get("orders", []):
            mode = "GÖNDERİLDİ" if result.get("approved") else "DRY-RUN"
            lines.append(f"- [{mode}] {o['side'].upper()} {o['ticker']} ${o['usd']}")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"congress_{result['asof']}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True, help="senate-stock-watcher aggregate JSON")
    ap.add_argument("--prices-json", default=None, help="{ticker:{YYYY-MM-DD:px}} (yoksa yfinance)")
    ap.add_argument("--asof", default=dt.date.today().isoformat())
    ap.add_argument("--approve", action="store_true",
                    help="paper emirleri GÖNDER (varsayılan dry-run)")
    ap.add_argument("--assumed-lag-days", type=int, default=DEFAULT_ASSUMED_LAG_DAYS)
    ap.add_argument("--leader-filter", default=None,
                    help="F6b: satır başına bir üye adı içeren dosya")
    ap.add_argument("--state", default=str(STATE_PATH))
    args = ap.parse_args()

    trades = load_trades(json.loads(pathlib.Path(args.data).read_text()))
    prices = (
        dict_price_provider(json.loads(pathlib.Path(args.prices_json).read_text()))
        if args.prices_json else yf_price_provider()
    )
    member_filter = None
    if args.leader_filter:
        member_filter = {
            l.strip() for l in pathlib.Path(args.leader_filter).read_text().splitlines()
            if l.strip()
        }

    if args.approve:
        from congress.alpaca import AlpacaPaper
        broker = AlpacaPaper()
    else:
        from congress.alpaca import FakeAlpaca
        broker = FakeAlpaca(equity=1000.0)

    state_path = pathlib.Path(args.state)
    state = load_state(state_path)
    result = run_once(
        trades, prices, broker, state, dt.date.fromisoformat(args.asof),
        assumed_lag_days=args.assumed_lag_days,
        member_filter=member_filter, approve=args.approve,
    )
    save_state(state, state_path)
    report = render_report(result)
    print(result["message"])
    print(f"rapor: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
