"""F6 testleri — docs/01 §3 kabul kriterleri + adversarial review bulgularının kilidi.

Her kritik bulgu için bir regresyon testi: phantom pozisyon (Sale Full→0), FIFO lot
eşleme (kısmi satış tüm pozisyonu kapatmaz), lider değişiminde eski pozisyon satışı,
kill-switch tasfiye + kalıcı halted, dry-run gerçek broker okuması, water-filling,
short-sell guard, pencere-filtreli min_trades.
"""

import datetime as dt
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from congress import mirror, models, ranking, run  # noqa: E402
from congress.alpaca import (  # noqa: E402
    AlpacaPaper, FakeAlpaca, NotPaperEndpointError, ShortSellBlockedError,
)

ASOF = dt.date(2026, 7, 1)


def _raw(member, ticker, ttype, amount, date):
    return {"senator": member, "ticker": ticker, "asset_type": "Stock",
            "type": ttype, "amount": amount, "transaction_date": date}


def _new_state():
    return {"positions": {}, "hwm": 0.0, "last_run": None, "member": None, "halted": False}


@pytest.fixture
def trades():
    raw = (
        [_raw("Uye A", "WIN", "Purchase", "$15,001 - $50,000", "01/15/2026")] * 6
        + [_raw("Uye A", "WIN", "Purchase", "$1,001 - $15,000", "02/10/2026")] * 4
        + [_raw("Uye B", "LOSE", "Purchase", "$15,001 - $50,000", "01/15/2026")] * 10
        + [{"senator": "Uye C", "ticker": "--", "asset_type": "Stock",
            "type": "Purchase", "amount": "$1,001 - $15,000",
            "transaction_date": "01/15/2026"},
           {"senator": "Uye C", "ticker": "BND", "asset_type": "Bond",
            "type": "Purchase", "amount": "$1,001 - $15,000",
            "transaction_date": "01/15/2026"}]
    )
    return models.load_trades(raw)


def _price_table(*tickers, start=dt.date(2026, 1, 1), slopes=None):
    slopes = slopes or {}
    table = {t: {} for t in tickers}
    d = start
    px = {t: 100.0 for t in tickers}
    while d <= ASOF:
        for t in tickers:
            table[t][d.isoformat()] = round(px[t], 2)
            px[t] += slopes.get(t, 0.5)
        d += dt.timedelta(days=1)
    return table


@pytest.fixture
def prices():
    return run.dict_price_provider(_price_table("WIN", "LOSE", slopes={"WIN": 0.5, "LOSE": -0.3}))


# ---------- models ----------

def test_amount_range_parsing():
    assert models.parse_amount_range("$1,001 - $15,000") == (1001.0, 15000.0, 8000.5)
    low, high, mid = models.parse_amount_range("$50,000,001 +")
    assert low == high == mid == 50000001.0


def test_normalize_filters_and_flags_full_exit():
    trades, dropped = models.load_trades_with_stats([
        _raw("X", "AAA", "Purchase", "$1,001 - $15,000", "01/15/2026"),
        _raw("X", "AAA", "Sale (Full)", "$1,001 - $15,000", "03/15/2026"),
        _raw("X", "AAA", "Sale (Partial)", "$1,001 - $15,000", "02/15/2026"),
        _raw("Y", "GOOD", "Purchase", "Unknown", "01/15/2026"),   # geçerli ticker, bozuk tutar
        {"senator": "Z", "ticker": "--", "asset_type": "Stock",
         "type": "Purchase", "amount": "$1,001 - $15,000", "transaction_date": "01/15/2026"},
    ])
    full = next(t for t in trades if t["raw_type"] == "Sale (Full)")
    partial = next(t for t in trades if t["raw_type"] == "Sale (Partial)")
    assert full["is_full_exit"] is True and partial["is_full_exit"] is False
    assert dropped.get("unparseable_amount") == 1  # 'Unknown'
    assert dropped.get("invalid_ticker") == 1      # '--'


def test_valid_dotted_ticker_survives():
    trades = models.load_trades([_raw("X", "BRK.B", "Purchase", "$1,001 - $15,000", "01/15/2026")])
    assert trades and trades[0]["ticker"] == "BRK.B"


# ---------- ranking: FIFO lot eşleme (bulgu #5) ----------

def test_partial_sale_does_not_close_whole_lot():
    """Küçük kısmi satış, büyük alımı 'kapandı' saymamalı; kalan asof'a kadar tutulur."""
    prices = run.dict_price_provider(_price_table("TICK", slopes={"TICK": 1.0}))
    # Ocak'ta büyük alım (efektif ~10 Şub), Mart'ta küçük kısmi satış (efektif ~Nis)
    trades = models.load_trades(
        [_raw("Z", "TICK", "Purchase", "$250,001 - $500,000", "01/15/2026")]
        + [_raw("Z", "TICK", "Sale (Partial)", "$1,001 - $15,000", "03/01/2026")] * 5
    )
    ranked = ranking.rank_members(trades, prices, ASOF, min_trades=1)
    # pozisyonun ezici çoğunluğu asof'a kadar tutulduğu için skor, yalnız kısmi
    # satış tarihindeki getiriden çok daha yüksek olmalı (fiyat yükseliyor)
    assert ranked[0]["score"] > 0.5  # asof'ta ~+%150; kısmi-only olsaydı ~+%5


# ---------- ranking: pencere-filtreli min_trades (bulgu #7) ----------

def test_min_trades_counts_only_window():
    prices = run.dict_price_provider(_price_table("OLD", "NEW"))
    trades = (
        # eski işlemler (5 yıl önce) — pencere DIŞI
        models.load_trades([_raw("Kidemli", "OLD", "Purchase", "$1,001 - $15,000", "01/15/2021")] * 20)
        # pencere İÇİ sadece 2
        + models.load_trades([_raw("Kidemli", "OLD", "Purchase", "$1,001 - $15,000", "05/01/2026")] * 2)
    )
    # all=22 ama window=2 -> min_trades=10 elemeli
    assert ranking.rank_members(trades, prices, ASOF, min_trades=10) == []
    assert ranking.rank_members(trades, prices, ASOF, min_trades=2)  # window=2 geçer


def test_ranking_disclosure_lagged(trades, prices):
    ranked = ranking.rank_members(trades, prices, ASOF, min_trades=5)
    assert [r["member"] for r in ranked] == ["Uye A", "Uye B"]
    assert ranked[0]["score"] > 0 > ranked[1]["score"]
    no_lag = ranking.rank_members(trades, prices, ASOF, min_trades=5, assumed_lag_days=0)
    assert ranked[0]["score"] < no_lag[0]["score"]


# ---------- mirror: phantom pozisyon (bulgu #6) ----------

def test_full_sale_zeroes_position_regardless_of_amount():
    """Fiyat düşünce Sale(Full) aralığı alımdan küçük olsa bile pozisyon KAPANIR."""
    # satış efektif tarihi (işlem + 26 gün) asof'tan ÖNCE olmalı ki görünsün
    t = models.load_trades([
        _raw("M", "XYZ", "Purchase", "$250,001 - $500,000", "01/10/2026"),   # mid ~375k
        _raw("M", "XYZ", "Sale (Full)", "$50,001 - $100,000", "05/10/2026"),  # mid ~75k, eff ~06/05
    ])
    pos = mirror.open_positions(t, "M", ASOF)
    assert "XYZ" not in pos  # dolar-farkı olsaydı +300k phantom kalırdı


def test_partial_then_full_and_rebuy():
    t = models.load_trades([
        _raw("M", "AAA", "Purchase", "$15,001 - $50,000", "01/10/2026"),
        _raw("M", "AAA", "Sale (Full)", "$15,001 - $50,000", "03/10/2026"),
        _raw("M", "AAA", "Purchase", "$1,001 - $15,000", "04/10/2026"),  # yeni pozisyon
    ])
    pos = mirror.open_positions(t, "M", ASOF)
    assert "AAA" in pos and pos["AAA"] == pytest.approx(8000.5)


# ---------- mirror: water-filling (bulgu #8) ----------

def test_water_filling_redistributes_overflow():
    # tek dev pozisyon + yeterli küçük pozisyon (>=8 pozisyon ki %80 investable
    # %10 tavanla dağıtılabilsin). Naif kod BIG'i %10'a kırpıp fazlayı dağıtmazdı.
    positions = {"BIG": 1_000_000.0}
    positions.update({f"S{i}": 20000.0 for i in range(8)})  # 9 pozisyon
    target = mirror.build_target_portfolio(positions, equity=1000.0)
    investable = 1000.0 * 0.80
    assert sum(target.values()) >= investable * 0.90  # su-doldurma çoğunu yatırır
    assert all(v <= 1000.0 * 0.10 + 0.01 for v in target.values())  # tavan korunur


def test_all_capped_leaves_reported_cash():
    # 2 pozisyon, ikisi de tavana takılır -> kalan nakit boşta, raporlanabilir
    target = mirror.build_target_portfolio({"A": 100.0, "B": 100.0}, equity=1000.0)
    assert mirror.uninvested_cash(target, 1000.0) > 0


def test_delta_idempotent_and_sell_before_buy():
    target = {"AAA": 100.0, "BBB": 80.0}
    assert mirror.compute_delta(target, dict(target)) == []
    orders = mirror.compute_delta({"CCC": 150.0}, {"AAA": 100.0})  # lider değişimi
    assert orders[0]["side"] == "sell"  # önce eski pozisyon satılır
    assert {o["ticker"] for o in orders} == {"AAA", "CCC"}


def test_kill_switch_threshold():
    assert mirror.kill_switch_triggered(850.0, 1000.0)
    assert not mirror.kill_switch_triggered(860.0, 1000.0)


# ---------- alpaca ----------

def test_paper_url_guard(monkeypatch):
    monkeypatch.setenv("ALPACA_BASE_URL", "https://api.alpaca.markets")
    with pytest.raises(NotPaperEndpointError):
        AlpacaPaper()


def test_fake_broker_blocks_short_sell():
    broker = FakeAlpaca(equity=1000.0, positions={"AAA": 50.0})
    with pytest.raises(ShortSellBlockedError):
        broker.submit_notional_order("AAA", 80.0, "sell")   # 80 > 50 -> short
    broker.submit_notional_order("AAA", 50.0, "sell")       # tam kapanış OK
    assert broker.positions_usd().get("AAA", 0.0) == pytest.approx(0.0)


# ---------- run: uçtan uca + kritik akışlar ----------

def test_run_once_dryrun_reads_real_broker(trades, prices):
    """[4] Dry-run gerçek broker'ı OKUR (sahte 1000 değil); emir GÖNDERMEZ."""
    broker = FakeAlpaca(equity=50000.0, positions={"OLD": 999.0})
    r = run.run_once(trades, prices, broker, _new_state(), ASOF, approve=False)
    assert r["equity"] == 50000.0 and broker.submitted == []       # okundu, gönderilmedi
    # dry-run önizlemesi gerçek OLD pozisyonunu görür -> onun için sell delta'sı var
    assert any(o["ticker"] == "OLD" and o["side"] == "sell" for o in r["orders"])


def test_run_once_idempotency_and_no_change(trades, prices):
    broker = FakeAlpaca(equity=1000.0)
    state = _new_state()
    r1 = run.run_once(trades, prices, broker, state, ASOF, approve=True)
    assert r1["member"] == "Uye A" and broker.submitted
    n = len(broker.submitted)
    r2 = run.run_once(trades, prices, broker, state, ASOF, approve=True)  # [2]
    assert len(broker.submitted) == n and r2["message"] == "Değişiklik yok."  # [4]


def test_leader_change_sells_old_positions(prices):
    """[3] Lider değişince eski üyenin pozisyonları SATILIR (çift portföy yok)."""
    # A: WIN yükselen (kazanır) -> ilk lider. Sonra veriye B'nin daha iyi hissesi eklenince
    # değil; bunun yerine iki ayrı koşuda farklı filtre ile lider değiştirelim.
    t_win = models.load_trades([_raw("A", "WIN", "Purchase", "$15,001 - $50,000", "01/15/2026")] * 10)
    t_meg = models.load_trades([_raw("B", "MEG", "Purchase", "$15,001 - $50,000", "01/15/2026")] * 10)
    px = run.dict_price_provider(_price_table("WIN", "MEG", slopes={"WIN": 0.5, "MEG": 2.0}))
    broker = FakeAlpaca(equity=1000.0)
    state = _new_state()

    # koşu 1: sadece A görünür -> WIN pozisyonu açılır
    run.run_once(t_win, px, broker, state, ASOF, approve=True)
    assert broker.positions_usd().get("WIN", 0) > 0
    # koşu 2: sadece B görünür -> yeni lider MEG; WIN İÇİN SELL üretilmeli
    r = run.run_once(t_meg, px, broker, state, ASOF, approve=True)
    assert any(o["ticker"] == "WIN" and o["side"] == "sell" for o in r["orders"])
    assert broker.positions_usd().get("WIN", 0.0) == pytest.approx(0.0)  # WIN kapandı
    assert broker.positions_usd().get("MEG", 0.0) > 0                    # MEG açıldı


def test_kill_switch_liquidates_and_stays_halted(trades, prices, tmp_path):
    """[3-kabul] Kill switch pozisyonları TASFİYE eder ve toparlansa bile HALTED kalır."""
    broker = FakeAlpaca(equity=1000.0)
    state = _new_state()
    run.run_once(trades, prices, broker, state, ASOF, approve=True)  # pozisyon aç, hwm=1000
    assert broker.positions_usd()  # açık pozisyon var

    broker._equity = 840.0  # HWM'den -%16
    r = run.run_once(trades, prices, broker, state, ASOF + dt.timedelta(days=1), approve=True)
    assert r["kill_switch"] and r["orders"]                       # tasfiye emirleri üretildi
    assert broker.positions_usd() == {}                          # gerçekten kapatıldı (bulgu #1)
    assert state["halted"] is True

    # equity toparlansa bile: hâlâ halted, işlem YOK (bulgu #2)
    broker._equity = 1000.0
    r2 = run.run_once(trades, prices, broker, state, ASOF + dt.timedelta(days=2), approve=True)
    assert r2.get("halted") and r2["orders"] == []
    assert "DURDURULDU" in r2["message"]

    text = run.render_report(r, out_dir=tmp_path).read_text()
    assert "KILL SWITCH" in text and "TASFİYE" in text and "45 gün" in text


def test_run_once_empty_ranking_and_report(prices, tmp_path):
    few = models.load_trades([_raw("Tek", "WIN", "Purchase", "$1,001 - $15,000", "01/15/2026")])
    r = run.run_once(few, prices, FakeAlpaca(), _new_state(), ASOF)
    assert "Sıralanabilir üye yok" in r["message"] and r["orders"] == []
    assert "45 gün" in run.render_report(r, out_dir=tmp_path).read_text()


def test_report_shows_dropped_and_cash(trades, prices, tmp_path):
    broker = FakeAlpaca(equity=1000.0)
    r = run.run_once(trades, prices, broker, _new_state(), ASOF,
                     dropped={"unparseable_amount": 3})
    text = run.render_report(r, out_dir=tmp_path).read_text()
    assert "unparseable_amount=3" in text


def test_price_provider_bridges_weekend_gaps():
    p = run.dict_price_provider({"AAA": {"2026-06-05": 10.0}})
    assert p("AAA", dt.date(2026, 6, 7)) == 10.0
    assert p("AAA", dt.date(2026, 6, 13)) is None
    assert p("YOK", dt.date(2026, 6, 7)) is None


def test_main_broker_selection_default_is_real(monkeypatch, tmp_path):
    """--fake-equity YOKSA AlpacaPaper okunmalı; --approve YOKKEN bile gerçek okuma."""
    import congress.alpaca as alp

    seen = {"paper": 0}

    class _PaperSpy:
        def __init__(self, *a, **k):
            seen["paper"] += 1
        def account_equity(self):
            return 5000.0
        def positions_usd(self):
            return {}
        def submit_notional_order(self, *a, **k):
            raise AssertionError("dry-run'da emir gönderilmemeli")

    monkeypatch.setattr(alp, "AlpacaPaper", _PaperSpy)
    data = tmp_path / "d.json"
    data.write_text(json.dumps([_raw("Uye A", "WIN", "Purchase", "$15,001 - $50,000", "01/15/2026")] * 10))
    pj = tmp_path / "p.json"
    pj.write_text(json.dumps(_price_table("WIN")))
    monkeypatch.setattr(sys, "argv", [
        "congress.run", "--data", str(data), "--prices-json", str(pj),
        "--asof", ASOF.isoformat(), "--state", str(tmp_path / "s.json"),
    ])
    monkeypatch.setattr(run, "REPORT_DIR", tmp_path / "reports")
    assert run.main() == 0
    assert seen["paper"] == 1  # gerçek broker okundu (dry-run'da bile), FakeAlpaca değil


def test_main_fake_equity_offline(monkeypatch, tmp_path):
    """--fake-equity: keysiz/ağsız simülasyon önizlemesi."""
    data = tmp_path / "d.json"
    data.write_text(json.dumps([_raw("Uye A", "WIN", "Purchase", "$15,001 - $50,000", "01/15/2026")] * 10))
    pj = tmp_path / "p.json"
    pj.write_text(json.dumps(_price_table("WIN")))
    monkeypatch.setattr(sys, "argv", [
        "congress.run", "--data", str(data), "--prices-json", str(pj),
        "--asof", ASOF.isoformat(), "--fake-equity", "2000", "--state", str(tmp_path / "s.json"),
    ])
    monkeypatch.setattr(run, "REPORT_DIR", tmp_path / "reports")
    assert run.main() == 0
    assert json.loads((tmp_path / "s.json").read_text())["hwm"] == 2000.0


def test_leader_filter_f6b(trades, prices):
    ranked = ranking.rank_members(trades, prices, ASOF, min_trades=5, member_filter={"Uye B"})
    assert [r["member"] for r in ranked] == ["Uye B"]
