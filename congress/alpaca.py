"""Alpaca PAPER API ince istemcisi.

SERT KURAL (docs/01 §3): base URL 'paper' içermiyorsa istemci HİÇ kurulmaz —
canlı endpoint'e karşı çalışmayı yapısal olarak engeller. Anahtarlar .env'den.
"""

from __future__ import annotations

import os

import requests


class NotPaperEndpointError(RuntimeError):
    pass


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

    def _get(self, path: str):
        r = requests.get(f"{self.base_url}{path}", headers=self._headers, timeout=30)
        r.raise_for_status()
        return r.json()

    def account_equity(self) -> float:
        return float(self._get("/v2/account")["equity"])

    def positions_usd(self) -> dict[str, float]:
        return {p["symbol"]: float(p["market_value"]) for p in self._get("/v2/positions")}

    def submit_notional_order(self, ticker: str, usd: float, side: str) -> dict:
        # v1: notional market/day emri. docs/01'deki limit ±%0.5 kuralından bilinçli
        # sapma — Alpaca notional emirle limit'i birleştirmez; paper fazında kabul,
        # canlı öncesi yeniden değerlendirilecek (rapora not düşülür).
        r = requests.post(
            f"{self.base_url}/v2/orders",
            headers=self._headers,
            json={"symbol": ticker, "notional": round(usd, 2), "side": side,
                  "type": "market", "time_in_force": "day"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()


class FakeAlpaca:
    """Test/dry-run ikamesi: emirleri sadece kaydeder."""

    def __init__(self, equity: float = 1000.0, positions: dict[str, float] | None = None):
        self._equity = equity
        self._positions = dict(positions or {})
        self.submitted: list[dict] = []

    def account_equity(self) -> float:
        return self._equity

    def positions_usd(self) -> dict[str, float]:
        return dict(self._positions)

    def submit_notional_order(self, ticker: str, usd: float, side: str) -> dict:
        order = {"symbol": ticker, "notional": round(usd, 2), "side": side}
        self.submitted.append(order)
        return order
