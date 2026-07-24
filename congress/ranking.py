"""Açıklama-tarihli sıralama metodolojisi (docs/01 §3'ün kod hali).

Kritik dürüstlük kuralı: getiriler işlem gününden değil, dışarıdan bir
kopyalayıcının işlemi GÖREBİLECEĞİ tarihten (açıklama tarihi; yoksa
transaction_date + assumed_lag_days) itibaren hesaplanır. Varsayılan 26 gün =
pratik medyan gecikme (kaynakça §7.2, tek çalışma — parametreyle değiştirilebilir).
"""

from __future__ import annotations

import datetime as dt
from typing import Callable

PriceProvider = Callable[[str, dt.date], float | None]

DEFAULT_ASSUMED_LAG_DAYS = 26


def effective_entry_date(trade: dict, assumed_lag_days: int = DEFAULT_ASSUMED_LAG_DAYS) -> dt.date:
    if trade.get("disclosure_date"):
        return trade["disclosure_date"]
    return trade["transaction_date"] + dt.timedelta(days=assumed_lag_days)


def _first_exit(trade: dict, sells: list[dict], entry: dt.date,
                assumed_lag_days: int) -> dt.date | None:
    """Aynı üye+ticker'da girişten SONRAKİ ilk satışın efektif tarihi."""
    candidates = [
        effective_entry_date(s, assumed_lag_days)
        for s in sells
        if s["ticker"] == trade["ticker"]
        and effective_entry_date(s, assumed_lag_days) > entry
    ]
    return min(candidates) if candidates else None


def rank_members(
    trades: list[dict],
    prices: PriceProvider,
    asof: dt.date,
    lookback_days: int = 365,
    min_trades: int = 10,
    assumed_lag_days: int = DEFAULT_ASSUMED_LAG_DAYS,
    member_filter: set[str] | None = None,
) -> list[dict]:
    """Üyeleri son 12 ayın açıklama-tarihli, tutar-ağırlıklı alım getirisiyle sıralar.

    member_filter: F6b lider-filtre deneyi için isim kümesi (None = herkes).
    Fiyatı bulunamayan işlemler sayılır ama getiriye katılmaz (skipped alanı).
    """
    window_start = asof - dt.timedelta(days=lookback_days)
    by_member: dict[str, dict] = {}

    for t in trades:
        m = t["member"]
        if member_filter and m not in member_filter:
            continue
        by_member.setdefault(m, {"buys": [], "sells": [], "all": 0})
        by_member[m]["all"] += 1
        (by_member[m]["buys"] if t["side"] == "buy" else by_member[m]["sells"]).append(t)

    results = []
    for member, g in by_member.items():
        if g["all"] < min_trades:
            continue
        weighted_ret, weight_sum, used, skipped = 0.0, 0.0, 0, 0
        for b in g["buys"]:
            entry = effective_entry_date(b, assumed_lag_days)
            if entry < window_start or entry > asof:
                continue
            exit_date = _first_exit(b, g["sells"], entry, assumed_lag_days) or asof
            exit_date = min(exit_date, asof)
            p_in = prices(b["ticker"], entry)
            p_out = prices(b["ticker"], exit_date)
            if not p_in or not p_out:
                skipped += 1
                continue
            weighted_ret += (p_out / p_in - 1.0) * b["amount_mid"]
            weight_sum += b["amount_mid"]
            used += 1
        if used == 0:
            continue
        results.append(
            {
                "member": member,
                "score": weighted_ret / weight_sum,
                "buys_used": used,
                "buys_skipped_no_price": skipped,
                "total_trades": g["all"],
            }
        )

    return sorted(results, key=lambda r: r["score"], reverse=True)
