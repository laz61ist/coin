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
    """senate-stock-watcher formatındaki tek kaydı normalize eder (yalnız Senato).

    NOT: bu şemada yalnızca 'senator' alanı vardır; House verisi ayrı bir kaynak
    ve parser gerektirir (docs/03 §F6 — hat şu an Senato-only). Hata sebeplerini
    ayırt etmek için ValueError yerine (None, reason) döndüren _try sürümü kullanılır.
    """
    result, _ = _try_normalize(record)
    return result


def _try_normalize(record: dict) -> tuple[dict | None, str | None]:
    if (record.get("asset_type") or "").strip() != "Stock":
        return None, "not_stock"
    ticker = (record.get("ticker") or "").strip()
    if not ticker or ticker in ("--", "N/A"):
        return None, "invalid_ticker"
    # meşru gösterim: harf(ler) + opsiyonel tek . veya - + harf(ler) (BRK.B, RDS-A)
    if not re.fullmatch(r"[A-Za-z]{1,6}([.\-][A-Za-z]{1,3})?", ticker):
        return None, "invalid_ticker"
    ttype_raw = (record.get("type") or "").strip()
    ttype = ttype_raw.lower()
    if "purchase" in ttype:
        side, is_full_exit = "buy", False
    elif "sale" in ttype:
        side = "sell"
        is_full_exit = "full" in ttype  # 'Sale (Full)' pozisyonu kapatır
    else:
        return None, "unknown_type"
    try:
        _, _, mid = parse_amount_range(record.get("amount", ""))
    except ValueError:
        return None, "unparseable_amount"
    try:
        tdate = _parse_date(record.get("transaction_date", ""))
    except ValueError:
        return None, "unparseable_date"
    member = (record.get("senator") or record.get("representative") or "").strip()
    if not member:
        return None, "no_member"
    return {
        "member": member,
        "ticker": ticker,
        "side": side,
        "is_full_exit": is_full_exit,
        "transaction_date": tdate,
        "disclosure_date": None,
        "amount_mid": mid,
        "raw_type": ttype_raw,
    }, None


def load_trades(records: list[dict]) -> list[dict]:
    """Geriye dönük uyumlu: yalnız geçerli kayıtları döndürür."""
    trades, _ = load_trades_with_stats(records)
    return trades


def load_trades_with_stats(records: list[dict]) -> tuple[list[dict], dict]:
    """Geçerli kayıtlar + hangi sebeple kaç kaydın düştüğünü raporlar (izlenebilirlik)."""
    out: list[dict] = []
    dropped: dict[str, int] = {}
    for r in records:
        n, reason = _try_normalize(r)
        if n is not None:
            out.append(n)
        else:
            dropped[reason] = dropped.get(reason, 0) + 1
    return out, dropped
