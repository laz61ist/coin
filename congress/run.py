"""F6 orkestratörü: veri -> sıralama -> hedef -> delta -> (dry-run | paper emir) -> rapor.

Kullanım:
  python3 -m congress.run --data all_transactions.json --prices-json fiyatlar.json          # DRY-RUN (gerçek hesabı OKUR, emir GÖNDERMEZ)
  python3 -m congress.run --data ... --prices-json ... --approve                             # paper emirleri gönder
  python3 -m congress.run --data ... --fake-equity 1000                                      # ağsız/keysiz simülasyon önizleme
  python3 -m congress.run --data ... --prices-json ... --leader-filter data/leaders.txt      # F6b deneyi

Broker gerçekliği: --fake-equity verilmedikçe HER ZAMAN gerçek Alpaca PAPER hesabı
okunur (dry-run'da bile equity/pozisyonlar gerçek). --approve yalnız EMİR GÖNDERİMİNİ
açar. Bu, 'dry-run gerçek hesaba dokunmasın' değil 'dry-run gerçek durumu doğru
önizlesin' ilkesidir (review bulgusu #4).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

from congress.mirror import (
    build_target_portfolio, compute_delta, kill_switch_triggered, open_positions,
    uninvested_cash,
)
from congress.models import load_trades_with_stats
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
        for i in range(1, 8):  # en yakın önceki işlem günü (hafta sonu/tatil köprüsü)
            k = (date - dt.timedelta(days=i)).isoformat()
            if k in series:
                return float(series[k])
        return None
    return provider


def yf_price_provider():
    import yfinance as yf

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
    return {"positions": {}, "hwm": 0.0, "last_run": None, "member": None, "halted": False}


def save_state(state: dict, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=1, ensure_ascii=False))


def _liquidation_orders(broker) -> list[dict]:
    return [{"ticker": t, "side": "sell", "usd": round(v, 2)}
            for t, v in broker.positions_usd().items() if v > 1e-9]


def run_once(
    trades: list[dict], prices, broker, state: dict, asof: dt.date,
    assumed_lag_days: int = DEFAULT_ASSUMED_LAG_DAYS,
    member_filter: set[str] | None = None,
    approve: bool = False,
    dropped: dict | None = None,
) -> dict:
    """Tek koşu; rapor sözlüğü döndürür. approve=False -> hiçbir emir gönderilmez."""
    base = {"asof": asof.isoformat(), "approved": approve, "dropped": dropped or {}}

    # Kalıcı durdurma (bulgu #2): kill switch bir kez tetiklendiyse equity toparlansa
    # bile manuel reset olmadan işlem YOK.
    if state.get("halted"):
        return {**base, "kill_switch": True, "halted": True, "orders": [], "ranking": [],
                "equity": broker.account_equity(),
                "message": "DURDURULDU: bot kill-switch sonrası halted. Devam için "
                           "state.json'da halted=false yapılmalı (manuel insan kararı)."}

    equity = broker.account_equity()
    hwm = max(state.get("hwm", 0.0), equity)

    if kill_switch_triggered(equity, state.get("hwm", 0.0)):
        liq = _liquidation_orders(broker)         # tasfiye emirleri (bulgu #1)
        if approve:
            for o in liq:
                broker.submit_notional_order(o["ticker"], o["usd"], "sell")
        state["halted"] = True                    # kalıcı durdurma (bulgu #2)
        state["positions"] = {} if approve else state.get("positions", {})
        state["hwm"] = hwm
        state["last_run"] = asof.isoformat()
        return {**base, "kill_switch": True, "halted": True, "equity": equity,
                "hwm": state.get("hwm"), "orders": liq, "ranking": [],
                "message": f"🛑 KILL SWITCH: equity HWM'den -%15+ düştü. "
                           f"{len(liq)} tasfiye emri {'GÖNDERİLDİ' if approve else 'ÖNERİLDİ (dry-run)'}; "
                           "bot halted, devam insan kararına bağlı (docs/03 §4 F3)."}

    ranking = rank_members(
        trades, prices, asof,
        assumed_lag_days=assumed_lag_days, member_filter=member_filter,
    )
    if not ranking:
        state["hwm"] = hwm
        state["last_run"] = asof.isoformat()
        return {**base, "kill_switch": False, "equity": equity, "orders": [], "ranking": [],
                "message": "Sıralanabilir üye yok (min işlem eşiği veya fiyat verisi yetersiz)."}

    top = ranking[0]["member"]
    positions = open_positions(trades, top, asof, assumed_lag_days)
    target = build_target_portfolio(positions, equity)
    # current = broker'ın GERÇEK pozisyonları (state değil) — lider değişince eski
    # tickerlar için otomatik SELL üretir, state driftini önler (bulgu #3 + #9)
    current = broker.positions_usd()
    orders = compute_delta(target, current)

    if approve and orders:
        for o in orders:
            broker.submit_notional_order(o["ticker"], o["usd"], o["side"])
        state["positions"] = broker.positions_usd()   # gerçekten oku, target'a güvenme
        state["member"] = top
    state["hwm"] = hwm
    state["last_run"] = asof.isoformat()

    return {
        **base, "kill_switch": False, "equity": equity, "member": top,
        "ranking": ranking[:10], "target": target,
        "uninvested_cash": uninvested_cash(target, equity),
        "orders": orders,
        "message": "Değişiklik yok." if not orders else f"{len(orders)} delta emri.",
    }


def render_report(result: dict, out_dir: pathlib.Path | None = None) -> pathlib.Path:
    out_dir = out_dir if out_dir is not None else REPORT_DIR
    lines = [f"# Kongre Kopyalama Raporu — {result['asof']}", "", LAG_WARNING, ""]
    if result.get("dropped"):
        drop = ", ".join(f"{k}={v}" for k, v in sorted(result["dropped"].items()))
        lines += [f"Elenen ham kayıt (sebep=adet): {drop}", ""]
    if result.get("kill_switch"):
        lines += [f"## 🛑 {result['message']}", f"- Equity: {result['equity']}",
                  f"- HWM: {result.get('hwm')}"]
        for o in result.get("orders", []):
            mode = "GÖNDERİLDİ" if result.get("approved") else "ÖNERİLDİ"
            lines.append(f"- [{mode}] TASFİYE SELL {o['ticker']} ${o['usd']}")
    else:
        lines += [f"Seçilen üye: **{result.get('member', '—')}** | Equity: {result['equity']}"]
        if result.get("uninvested_cash", 0) > 0:
            lines.append(f"⚠️ Yatırılamayan bakiye (tavan doygunluğu): ${result['uninvested_cash']}")
        lines += ["", "| # | Üye | Skor | Kullanılan lot | Fiyatsız atlanan | Pencere işlemi |",
                  "|---|---|---|---|---|---|"]
        for i, r in enumerate(result.get("ranking", []), 1):
            lines.append(
                f"| {i} | {r['member']} | {r['score'] * 100:.1f}% | {r['lots_used']} "
                f"| {r['lots_skipped_no_price']} | {r['window_trades']} |"
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
    ap.add_argument("--approve", action="store_true", help="paper emirleri GÖNDER")
    ap.add_argument("--fake-equity", type=float, default=None,
                    help="ağsız/keysiz simülasyon: gerçek Alpaca yerine bu equity ile FakeAlpaca")
    ap.add_argument("--assumed-lag-days", type=int, default=DEFAULT_ASSUMED_LAG_DAYS)
    ap.add_argument("--leader-filter", default=None, help="F6b: satır başına bir üye adı")
    ap.add_argument("--state", default=str(STATE_PATH))
    args = ap.parse_args()

    trades, dropped = load_trades_with_stats(json.loads(pathlib.Path(args.data).read_text()))
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

    if args.fake_equity is not None:
        from congress.alpaca import FakeAlpaca
        broker = FakeAlpaca(equity=args.fake_equity)   # açık simülasyon
    else:
        from congress.alpaca import AlpacaPaper
        broker = AlpacaPaper()                          # dry-run'da bile gerçek OKUMA

    state_path = pathlib.Path(args.state)
    state = load_state(state_path)
    result = run_once(
        trades, prices, broker, state, dt.date.fromisoformat(args.asof),
        assumed_lag_days=args.assumed_lag_days, member_filter=member_filter,
        approve=args.approve, dropped=dropped,
    )
    save_state(state, state_path)
    report = render_report(result)
    print(result["message"])
    print(f"rapor: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
