"""Açıklama-tarihli sıralama metodolojisi (docs/01 §3'ün kod hali).

Kritik dürüstlük kuralları:
- Getiriler işlem gününden değil, dışarıdan bir kopyalayıcının işlemi
  GÖREBİLECEĞİ tarihten (açıklama tarihi; yoksa transaction_date +
  assumed_lag_days) itibaren hesaplanır. Varsayılan 26 gün = pratik medyan
  gecikme (kaynakça §7.2).
- FIFO lot eşleme: her satış açık alım lotlarını miktarına göre sırayla kapatır;
  kısmi satış tüm pozisyonu kapatmış SAYILMAZ (review bulgusu #5).
- min_trades eşiği yalnız pencere-içi (son 12 ay) işlemlere uygulanır (bulgu #7).
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


def _closed_lots(buys: list[dict], sells: list[dict], asof: dt.date,
                 assumed_lag_days: int) -> list[tuple[dict, dt.date, float]]:
    """FIFO ile her alım lotunun (trade, exit_date, kapanan_pay_oranı) parçalarını üretir.

    Bir alım birden çok satışla kısmen kapanabilir; kapanmayan kalan pay asof'ta
    (hâlâ elde) kapanmış sayılır. Dönen liste: (buy_trade, exit_date, weight_fraction).
    weight_fraction toplamı her alım için 1.0'dır (tam muhasebe).
    """
    open_buys = sorted(
        ({"t": b, "remaining": b["amount_mid"],
          "entry": effective_entry_date(b, assumed_lag_days)} for b in buys),
        key=lambda x: x["entry"],
    )
    sell_events = sorted(
        ((effective_entry_date(s, assumed_lag_days), s["amount_mid"]) for s in sells),
        key=lambda x: x[0],
    )
    lots: list[tuple[dict, dt.date, float]] = []

    for sell_date, sell_amt in sell_events:
        for ob in open_buys:
            if sell_amt <= 1e-9:
                break
            # sadece satıştan önce girilmiş ve hâlâ açık olan lotları kapat
            if ob["remaining"] <= 1e-9 or ob["entry"] > sell_date:
                continue
            closed = min(ob["remaining"], sell_amt)
            frac = closed / ob["t"]["amount_mid"]
            lots.append((ob["t"], sell_date, frac))
            ob["remaining"] -= closed
            sell_amt -= closed

    # kapanmayan kalanlar asof'ta (hâlâ elde) kapanmış varsay
    for ob in open_buys:
        if ob["remaining"] > 1e-9:
            frac = ob["remaining"] / ob["t"]["amount_mid"]
            lots.append((ob["t"], asof, frac))
    return lots


def rank_members(
    trades: list[dict],
    prices: PriceProvider,
    asof: dt.date,
    lookback_days: int = 365,
    min_trades: int = 10,
    assumed_lag_days: int = DEFAULT_ASSUMED_LAG_DAYS,
    member_filter: set[str] | None = None,
) -> list[dict]:
    """Üyeleri son 12 ayın açıklama-tarihli, tutar-ağırlıklı, FIFO-lotlu alım getirisiyle sıralar.

    member_filter: F6b lider-filtre deneyi (None = herkes).
    Fiyatı bulunamayan lotlar sayılır ama getiriye katılmaz (skipped alanı).
    """
    window_start = asof - dt.timedelta(days=lookback_days)
    by_member: dict[str, dict] = {}

    for t in trades:
        m = t["member"]
        if member_filter and m not in member_filter:
            continue
        g = by_member.setdefault(m, {"buys": [], "sells": [], "window_count": 0})
        entry = effective_entry_date(t, assumed_lag_days)
        if window_start <= entry <= asof:
            g["window_count"] += 1
        (g["buys"] if t["side"] == "buy" else g["sells"]).append(t)

    results = []
    for member, g in by_member.items():
        if g["window_count"] < min_trades:  # yalnız pencere-içi sayım (bulgu #7)
            continue
        weighted_ret, weight_sum, used, skipped = 0.0, 0.0, 0, 0
        for buy, exit_date, frac in _closed_lots(g["buys"], g["sells"], asof, assumed_lag_days):
            entry = effective_entry_date(buy, assumed_lag_days)
            if not (window_start <= entry <= asof):
                continue
            exit_date = min(exit_date, asof)
            p_in = prices(buy["ticker"], entry)
            p_out = prices(buy["ticker"], exit_date)
            if not p_in or not p_out:
                skipped += 1
                continue
            lot_weight = buy["amount_mid"] * frac
            weighted_ret += (p_out / p_in - 1.0) * lot_weight
            weight_sum += lot_weight
            used += 1
        if used == 0:
            continue
        results.append(
            {
                "member": member,
                "score": weighted_ret / weight_sum,
                "lots_used": used,
                "lots_skipped_no_price": skipped,
                "window_trades": g["window_count"],
            }
        )

    return sorted(results, key=lambda r: r["score"], reverse=True)
