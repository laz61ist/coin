"""Aynalama kuralları: hedef portföy, delta emirler, kill switch (docs/01 §3)."""

from __future__ import annotations

import datetime as dt

from congress.ranking import DEFAULT_ASSUMED_LAG_DAYS, effective_entry_date

MAX_WEIGHT = 0.10      # ticker başına maks özkaynak payı
CASH_BUFFER = 0.20     # yatırılmayan nakit tamponu
MIN_ORDER_USD = 25.0   # bunun altındaki delta gürültüdür, emir üretmez
KILL_DRAWDOWN = 0.15   # HWM'den bu kadar düşüş -> tasfiye + dur


def open_positions(
    trades: list[dict], member: str, asof: dt.date,
    assumed_lag_days: int = DEFAULT_ASSUMED_LAG_DAYS,
) -> dict[str, float]:
    """Üyenin asof itibarıyla AÇIK görünen long pozisyonları (midpoint USD, net)."""
    net: dict[str, float] = {}
    for t in sorted(
        (x for x in trades if x["member"] == member),
        key=lambda x: effective_entry_date(x, assumed_lag_days),
    ):
        if effective_entry_date(t, assumed_lag_days) > asof:
            continue
        delta = t["amount_mid"] if t["side"] == "buy" else -t["amount_mid"]
        net[t["ticker"]] = net.get(t["ticker"], 0.0) + delta
    return {k: v for k, v in net.items() if v > 0}


def build_target_portfolio(
    positions: dict[str, float], equity: float,
    max_weight: float = MAX_WEIGHT, cash_buffer: float = CASH_BUFFER,
) -> dict[str, float]:
    """Midpoint ağırlıklarını hesaba oranlar; ticker tavanı + nakit tamponu uygular."""
    total = sum(positions.values())
    if total <= 0 or equity <= 0:
        return {}
    investable = equity * (1.0 - cash_buffer)
    target = {
        t: min(investable * (v / total), equity * max_weight)
        for t, v in positions.items()
    }
    return {t: round(usd, 2) for t, usd in target.items() if usd >= MIN_ORDER_USD}


def compute_delta(
    target: dict[str, float], current: dict[str, float],
    min_order_usd: float = MIN_ORDER_USD,
) -> list[dict]:
    """Sadece FARKI emirle (idempotency): aynı hedefe ikinci koşu sıfır emir üretir."""
    orders = []
    for ticker in sorted(set(target) | set(current)):
        diff = target.get(ticker, 0.0) - current.get(ticker, 0.0)
        if abs(diff) < min_order_usd:
            continue
        orders.append(
            {"ticker": ticker, "side": "buy" if diff > 0 else "sell",
             "usd": round(abs(diff), 2)}
        )
    return orders


def kill_switch_triggered(
    equity: float, high_water_mark: float, threshold: float = KILL_DRAWDOWN
) -> bool:
    return high_water_mark > 0 and equity <= high_water_mark * (1.0 - threshold)
