"""Ham açıklama kayıtlarını normalize eden saf yardımcılar."""

from __future__ import annotations

import datetime as dt
import re

# STOCK Act beyanları tutar değil ARALIK verir; orta nokta kullanılır (docs/01 §3)
_AMOUNT_RE = re.compile(r"\$([\d,]+)(?:\s*-\s*\$([\d,]+))?")


def parse_amount_range(text: str) -> tuple[float, float, float]:
    """'$15,001 - $50,000' -> (low, high, mid); '$50,000,001 +' -> (low, low, low)."""
    m = _AMOUNT_RE.search(text or "")
    if not m:
        raise ValueError(f"tutar aralığı çözülemedi: {text!r}")
    low = float(m.group(1).replace(",", ""))
    high = float(m.group(2).replace(",", "")) if m.group(2) else low
    return low, high, (low + high) / 2


def _parse_date(text: str) -> dt.date:
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"tarih çözülemedi: {text!r}")


def normalize_senate_watcher(record: dict) -> dict | None:
    """senate-stock-watcher formatındaki tek kaydı normalize eder.

    Sadece hisse (Stock) ve geçerli ticker'lı kayıtlar; diğerleri None.
    disclosure_date bu veri setinde yok -> None (ranking varsayılan gecikme uygular).
    """
    if (record.get("asset_type") or "").strip() != "Stock":
        return None
    ticker = (record.get("ticker") or "").strip()
    if not ticker or ticker in ("--", "N/A") or len(ticker) > 6:
        return None
    ttype = (record.get("type") or "").lower()
    if "purchase" in ttype:
        side = "buy"
    elif "sale" in ttype:
        side = "sell"
    else:
        return None
    try:
        _, _, mid = parse_amount_range(record.get("amount", ""))
        tdate = _parse_date(record.get("transaction_date", ""))
    except ValueError:
        return None
    return {
        "member": (record.get("senator") or record.get("representative") or "").strip(),
        "ticker": ticker,
        "side": side,
        "transaction_date": tdate,
        "disclosure_date": None,
        "amount_mid": mid,
    }


def load_trades(records: list[dict]) -> list[dict]:
    out = []
    for r in records:
        n = normalize_senate_watcher(r)
        if n and n["member"]:
            out.append(n)
    return out
