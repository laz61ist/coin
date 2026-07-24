"""F6 testleri — docs/01 §3 kabul kriterlerinin kod karşılıkları:
[1] dry-run gerçekçi veriden sıralama + emir listesi üretir
[2] aynı gün ikinci koşu sıfır çift emir (idempotency)
[3] kill switch simüle -%15'te tetiklenir
[4] değişiklik yoksa rapor 'Değişiklik yok' der
+ her raporda 45-gün şerhi, paper-URL bekçisi, açıklama-gecikmeli metodoloji.
"""

import datetime as dt
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from congress import mirror, models, ranking, run  # noqa: E402
from congress.alpaca import AlpacaPaper, FakeAlpaca, NotPaperEndpointError  # noqa: E402

ASOF = dt.date(2026, 7, 1)


def _raw(member, ticker, ttype, amount, date):
    return {"senator": member, "ticker": ticker, "asset_type": "Stock",
            "type": ttype, "amount": amount, "transaction_date": date}


@pytest.fixture
def trades():
    raw = (
        # A üyesi: 10+ işlem, WIN hissesinde erken alım (yükselen fiyat)
        [_raw("Uye A", "WIN", "Purchase", "$15,001 - $50,000", "01/15/2026")] * 6
        + [_raw("Uye A", "WIN", "Purchase", "$1,001 - $15,000", "02/10/2026")] * 4
        # B üyesi: LOSE hissesinde alım (düşen fiyat)
        + [_raw("Uye B", "LOSE", "Purchase", "$15,001 - $50,000", "01/15/2026")] * 10
        # gürültü: hisse olmayan + bozuk ticker (normalize elemeli)
        + [{"senator": "Uye C", "ticker": "--", "asset_type": "Stock",
            "type": "Purchase", "amount": "$1,001 - $15,000",
            "transaction_date": "01/15/2026"},
           {"senator": "Uye C", "ticker": "BND", "asset_type": "Bond",
            "type": "Purchase", "amount": "$1,001 - $15,000",
            "transaction_date": "01/15/2026"}]
    )
    return models.load_trades(raw)


@pytest.fixture
def prices():
    # WIN doğrusal yükselir, LOSE düşer; her takvim günü fiyat var
    table = {"WIN": {}, "LOSE": {}}
    d = dt.date(2026, 1, 1)
    px_w, px_l = 100.0, 100.0
    while d <= ASOF:
        table["WIN"][d.isoformat()] = round(px_w, 2)
        table["LOSE"][d.isoformat()] = round(px_l, 2)
        px_w += 0.5
        px_l -= 0.3
        d += dt.timedelta(days=1)
    return run.dict_price_provider(table)


def test_amount_range_parsing():
    assert models.parse_amount_range("$1,001 - $15,000") == (1001.0, 15000.0, 8000.5)
    low, high, mid = models.parse_amount_range("$50,000,001 +")
    assert low == high == mid == 50000001.0


def test_normalize_filters_noise(trades):
    members = {t["member"] for t in trades}
    assert members == {"Uye A", "Uye B"}  # C'nin iki kaydı da elendi


def test_ranking_disclosure_lagged_and_ordered(trades, prices):
    ranked = ranking.rank_members(trades, prices, ASOF, min_trades=5)
    assert [r["member"] for r in ranked] == ["Uye A", "Uye B"]
    assert ranked[0]["score"] > 0 > ranked[1]["score"]
    # açıklama gecikmesi: giriş 15 Ocak DEĞİL, +26 gün sonrası -> skor, işlem-günü
    # girişe göre daha düşük olmalı (yükselen hissede geç giriş)
    ranked_no_lag = ranking.rank_members(trades, prices, ASOF, min_trades=5,
                                         assumed_lag_days=0)
    assert ranked[0]["score"] < ranked_no_lag[0]["score"]


def test_open_positions_nets_sells():
    t = models.load_trades([
        _raw("X", "AAA", "Purchase", "$15,001 - $50,000", "01/10/2026"),
        _raw("X", "AAA", "Sale (Full)", "$15,001 - $50,000", "03/10/2026"),
        _raw("X", "BBB", "Purchase", "$1,001 - $15,000", "01/10/2026"),
    ])
    pos = mirror.open_positions(t, "X", ASOF)
    assert "AAA" not in pos and "BBB" in pos


def test_target_portfolio_caps_and_cash_buffer():
    target = mirror.build_target_portfolio(
        {"AAA": 90000.0, "BBB": 10000.0}, equity=1000.0
    )
    assert sum(target.values()) <= 1000.0 * 0.80 + 0.01     # nakit tamponu
    assert target["AAA"] <= 1000.0 * 0.10 + 0.01            # ticker tavanı
    assert "BBB" in target


def test_delta_idempotent_and_min_order():
    target = {"AAA": 100.0, "BBB": 80.0}
    assert mirror.compute_delta(target, dict(target)) == []          # [2] çift emir yok
    orders = mirror.compute_delta(target, {"AAA": 100.0, "BBB": 70.0})
    assert orders == []                                              # 10$ < eşik
    orders = mirror.compute_delta(target, {})
    assert {o["ticker"] for o in orders} == {"AAA", "BBB"}


def test_kill_switch_threshold():
    assert mirror.kill_switch_triggered(equity=850.0, high_water_mark=1000.0)
    assert not mirror.kill_switch_triggered(equity=860.0, high_water_mark=1000.0)


def test_paper_url_guard(monkeypatch):
    monkeypatch.setenv("ALPACA_BASE_URL", "https://api.alpaca.markets")
    with pytest.raises(NotPaperEndpointError):
        AlpacaPaper()


def test_run_once_end_to_end(trades, prices, tmp_path):
    broker = FakeAlpaca(equity=1000.0)
    state = {"positions": {}, "hwm": 0.0, "last_run": None, "member": None}

    # [1] dry-run: sıralama + emir listesi var, emir GÖNDERİLMEDİ
    r1 = run.run_once(trades, prices, broker, state, ASOF, approve=False)
    assert r1["member"] == "Uye A" and r1["orders"] and broker.submitted == []

    # onaylı koşu: emirler gönderilir, state hedefe eşitlenir
    r2 = run.run_once(trades, prices, broker, state, ASOF, approve=True)
    assert broker.submitted and state["positions"] == r2["target"]

    # [2] aynı gün üçüncü koşu: sıfır yeni emir + 'Değişiklik yok'
    n_before = len(broker.submitted)
    r3 = run.run_once(trades, prices, broker, state, ASOF, approve=True)
    assert len(broker.submitted) == n_before
    assert r3["message"] == "Değişiklik yok."                        # [4]

    # rapor: 45-gün şerhi HER raporda
    report = run.render_report(r3, out_dir=tmp_path)
    text = report.read_text()
    assert "45 gün" in text and "Değişiklik yok" in text

    # [3] kill switch: equity HWM'den -%15'in altına düşer
    poor = FakeAlpaca(equity=840.0)
    r4 = run.run_once(trades, prices, poor, state, ASOF + dt.timedelta(days=1))
    assert r4["kill_switch"] and r4["orders"] == []
    ks_report = run.render_report(r4, out_dir=tmp_path).read_text()
    assert "KILL SWITCH" in ks_report and "45 gün" in ks_report


def test_leader_filter_f6b(trades, prices):
    ranked = ranking.rank_members(trades, prices, ASOF, min_trades=5,
                                  member_filter={"Uye B"})
    assert [r["member"] for r in ranked] == ["Uye B"]
