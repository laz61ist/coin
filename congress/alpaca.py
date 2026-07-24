"""Alpaca PAPER API ince istemcisi.

SERT KURAL (docs/01 §3): base URL 'paper' içermiyorsa istemci HİÇ kurulmaz —
canlı endpoint'e karşı çalışmayı yapısal olarak engeller. Anahtarlar .env'den.
"""

from __future__ import annotations

import os
import time

import requests

_RETRY_STATUS = {429, 500, 502, 503, 504}


class NotPaperEndpointError(RuntimeError):
    pass


class ShortSellBlockedError(RuntimeError):
    """Yalnız-long mirror kuralı: mevcut pozisyondan fazla satış short açardı."""


def _request_with_retry(method, url, *, headers, json=None, timeout=30, retries=3):
    last = None
    for attempt in range(retries):
        try:
            r = requests.request(method, url, headers=headers, json=json, timeout=timeout)
            if r.status_code in _RETRY_STATUS:
                last = requests.HTTPError(f"{r.status_code} retryable", response=r)
            else:
                r.raise_for_status()
                return r
        except (requests.ConnectionError, requests.Timeout) as exc:
            last = exc
        if attempt < retries - 1:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
    if isinstance(last, requests.HTTPError):
        last.response.raise_for_status()
    raise last


class AlpacaPaper:
    def __init__(self, base_url: str | None = None,
                 key_id: str | None = None, secret: str | None = None):
        self.base_url = (base_url or os.getenv("ALPACA_BASE_URL", "")).rstrip("/")
        if "paper" not in self.base_url:
            raise NotPaperEndpointError(
                f"ALPACA_BASE_URL 'paper' içermiyor: {self.base_url!r} — "
                "canlı endpoint'e karşı çalışmak yasak (docs/01 §3)"
            )
        self._headers = {
            "APCA-API-KEY-ID": key_id or os.getenv("ALPACA_KEY_ID", ""),
            "APCA-API-SECRET-KEY": secret or os.getenv("ALPACA_SECRET_KEY", ""),
        }

    def account_equity(self) -> float:
        r = _request_with_retry("GET", f"{self.base_url}/v2/account", headers=self._headers)
        return float(r.json()["equity"])

    def positions_usd(self) -> dict[str, float]:
        r = _request_with_retry("GET", f"{self.base_url}/v2/positions", headers=self._headers)
        return {p["symbol"]: float(p["market_value"]) for p in r.json()}

    def submit_notional_order(self, ticker: str, usd: float, side: str) -> dict:
        # Yalnız-long guard: sell tutarı mevcut pozisyonu aşamaz (short'u engelle, bulgu #13)
        if side == "sell":
            held = self.positions_usd().get(ticker, 0.0)
            if usd > held + 1e-6:
                raise ShortSellBlockedError(
                    f"{ticker}: sell ${usd} > mevcut ${held}; yalnız-long kuralı"
                )
        r = _request_with_retry(
            "POST", f"{self.base_url}/v2/orders", headers=self._headers,
            json={"symbol": ticker, "notional": round(usd, 2), "side": side,
                  "type": "market", "time_in_force": "day"},
        )
        return r.json()


class FakeAlpaca:
    """Test/dry-run ikamesi: pozisyonları gerçekçi tutar (buy artırır, sell azaltır)."""

    def __init__(self, equity: float = 1000.0, positions: dict[str, float] | None = None):
        self._equity = equity
        self._positions = dict(positions or {})
        self.submitted: list[dict] = []

    def account_equity(self) -> float:
        return self._equity

    def positions_usd(self) -> dict[str, float]:
        return {k: v for k, v in self._positions.items() if v > 1e-9}

    def submit_notional_order(self, ticker: str, usd: float, side: str) -> dict:
        held = self._positions.get(ticker, 0.0)
        if side == "sell" and usd > held + 1e-6:
            raise ShortSellBlockedError(f"{ticker}: sell ${usd} > mevcut ${held}")
        self._positions[ticker] = held + usd if side == "buy" else held - usd
        order = {"symbol": ticker, "notional": round(usd, 2), "side": side, "status": "filled"}
        self.submitted.append(order)
        return order
