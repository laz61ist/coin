"""Aynalama kuralları: hedef portföy, delta emirler, kill switch (docs/01 §3)."""

from __future__ import annotations

import datetime as dt

from congress.ranking import DEFAULT_ASSUMED_LAG_DAYS, effective_entry_date

MAX_WEIGHT = 0.10        # ticker başına maks özkaynak payı
CASH_BUFFER = 0.20       # yatırılmayan nakit tamponu
INCLUDE_MIN_USD = 25.0   # hedef portföye dahil etme eşiği (mutlak)
DELTA_MIN_USD = 40.0     # emir tetikleme eşiği (histerezis — churn önler, bulgu #12)
KILL_DRAWDOWN = 0.15     # HWM'den bu kadar düşüş -> tasfiye + dur


def open_positions(
    trades: list[dict], member: str, asof: dt.date,
    assumed_lag_days: int = DEFAULT_ASSUMED_LAG_DAYS,
) -> dict[str, float]:
    """Üyenin asof itibarıyla AÇIK görünen long pozisyonları (midpoint USD).

    'Sale (Full)' bir tickerda görüldüğünde o ticker DOĞRUDAN sıfırlanır — dolar
    farkı netlemesi değil (fiyat değişimi phantom pozisyon üretiyordu, bulgu #6).
    Sıfırlama sonrası yeni alımlar yeni pozisyon olarak birikir.
    """
    net: dict[str, float] = {}
    for t in sorted(
        (x for x in trades if x["member"] == member),
        key=lambda x: effective_entry_date(x, assumed_lag_days),
    ):
        if effective_entry_date(t, assumed_lag_days) > asof:
            continue
        tk = t["ticker"]
        if t["side"] == "buy":
            net[tk] = net.get(tk, 0.0) + t["amount_mid"]
        elif t.get("is_full_exit"):
            net[tk] = 0.0                       # tam satış -> pozisyon kapanır
        else:
            net[tk] = net.get(tk, 0.0) - t["amount_mid"]  # kısmi satış -> azalt
    return {k: v for k, v in net.items() if v > 1e-9}


def build_target_portfolio(
    positions: dict[str, float], equity: float,
    max_weight: float = MAX_WEIGHT, cash_buffer: float = CASH_BUFFER,
    include_min_usd: float = INCLUDE_MIN_USD,
) -> dict[str, float]:
    """Midpoint ağırlıklarını hesaba oranlar; ticker tavanı + nakit tamponu +
    water-filling (tavana takılan fazla payı diğerlerine yeniden dağıt, bulgu #8)."""
    if equity <= 0:
        return {}
    total = sum(positions.values())
    if total <= 0:
        return {}
    investable = equity * (1.0 - cash_buffer)
    cap = equity * max_weight
    # her ticker tavanı aşamaz; toplam yatırılabilir cap*n'i aşamaz
    weights = {t: v / total for t, v in positions.items()}
    alloc = {t: investable * w for t, w in weights.items()}

    # su-doldurma: tavanı aşanları kırp, artan payı kırpılmamışlara oranla dağıt
    for _ in range(len(alloc) + 1):
        capped = {t: a for t, a in alloc.items() if a > cap + 1e-9}
        if not capped:
            break
        overflow = sum(a - cap for t, a in capped.items())
        for t in capped:
            alloc[t] = cap
        free = {t: a for t, a in alloc.items() if a < cap - 1e-9}
        free_sum = sum(free.values())
        if free_sum <= 1e-9:
            break  # dağıtılacak yer yok (hepsi tavanda) -> kalan nakit boşta
        for t in free:
            alloc[t] = min(cap, alloc[t] + overflow * (free[t] / free_sum))

    return {t: round(a, 2) for t, a in alloc.items() if a >= include_min_usd}


def uninvested_cash(target: dict[str, float], equity: float) -> float:
    """Water-filling sonrası yatırılamayan (tavan doygunluğu) bakiye — raporlanır."""
    investable = equity * (1.0 - CASH_BUFFER)
    return round(max(0.0, investable - sum(target.values())), 2)


def compute_delta(
    target: dict[str, float], current: dict[str, float],
    delta_min_usd: float = DELTA_MIN_USD,
) -> list[dict]:
    """Sadece FARKI emirle (idempotency): aynı hedefe ikinci koşu sıfır emir üretir.
    Emirler ÖNCE satışlar sonra alımlar sıralı (alım gücü açılsın, bulgu #3)."""
    orders = []
    for ticker in sorted(set(target) | set(current)):
        diff = target.get(ticker, 0.0) - current.get(ticker, 0.0)
        if abs(diff) < delta_min_usd:
            continue
        orders.append(
            {"ticker": ticker, "side": "buy" if diff > 0 else "sell",
             "usd": round(abs(diff), 2)}
        )
    orders.sort(key=lambda o: 0 if o["side"] == "sell" else 1)
    return orders


def kill_switch_triggered(
    equity: float, high_water_mark: float, threshold: float = KILL_DRAWDOWN
) -> bool:
    return high_water_mark > 0 and equity <= high_water_mark * (1.0 - threshold)
