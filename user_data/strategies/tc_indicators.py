"""Trader Club 5in1 göstergelerinin repaint'siz Python portu.

Kaynak analiz: docs/04-pine-inceleme.md. Kurallar:
- Her sinyal bar kapanışında kesinleşir; hiçbir fonksiyon gelecekteki barı okumaz.
- Nadaraya-Watson ve Linreg SADECE endpoint (bar-kapanış) versiyonlarıyla port edildi;
  Pine'daki repaint modları bilinçli olarak YOK (docs/04 §R1, §R3).
- PMax'taki CMO penceresi Pine orijinaline sadakat için 9 sabitiyle bırakıldı (docs/04 §B5);
  değiştirmek istersen cmo_window parametresi var.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ---------- temel bloklar ----------

def wma(series: pd.Series, length: int) -> pd.Series:
    weights = np.arange(1, length + 1, dtype=float)
    return series.rolling(length).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )


def rma(series: pd.Series, length: int) -> pd.Series:
    # Pine ta.rma / ta.atr'nin kullandığı Wilder ortalaması
    return series.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()


def atr(df: pd.DataFrame, length: int = 10) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return rma(tr, length)


# ---------- 1) MavilimW ----------

def mavilim(close: pd.Series, fmal: int = 3, smal: int = 5) -> pd.Series:
    """İç içe 6 WMA zinciri (3,5,8,13,21,34 Fibonacci uzunlukları)."""
    tmal = fmal + smal
    Fmal = smal + tmal
    Ftmal = tmal + Fmal
    Smal = Fmal + Ftmal
    m = wma(close, fmal)
    m = wma(m, smal)
    m = wma(m, tmal)
    m = wma(m, Fmal)
    m = wma(m, Ftmal)
    return wma(m, Smal)


# ---------- 2) PMax ----------

def pmax(
    df: pd.DataFrame,
    atr_length: int = 10,
    multiplier: float = 3.0,
    ma_length: int = 9,
    ma_type: str = "EMA",
    cmo_window: int = 9,
) -> pd.DataFrame:
    """ATR trailing stop (supertrend varyantı, MA üstüne).

    Döner: DataFrame(pmax, pmax_ma, pmax_dir) — dir: 1 long rejim, -1 short rejim.
    """
    src = (df["high"] + df["low"]) / 2
    _atr = atr(df, atr_length)

    if ma_type == "EMA":
        mavg = src.ewm(span=ma_length, adjust=False).mean()
    elif ma_type == "SMA":
        mavg = src.rolling(ma_length).mean()
    elif ma_type == "WMA":
        mavg = wma(src, ma_length)
    elif ma_type == "VAR":  # Pine'daki VAR (CMO-ağırlıklı VIDYA)
        valpha = 2.0 / (ma_length + 1)
        diff = src.diff()
        vud = diff.clip(lower=0).rolling(cmo_window).sum()
        vdd = (-diff.clip(upper=0)).rolling(cmo_window).sum()
        vcmo = ((vud - vdd) / (vud + vdd)).abs().fillna(0.0)
        out = np.zeros(len(src))
        s = src.to_numpy()
        k = vcmo.to_numpy()
        for i in range(1, len(s)):
            a = valpha * k[i]
            out[i] = a * s[i] + (1 - a) * out[i - 1]
        mavg = pd.Series(out, index=src.index)
    else:
        raise ValueError(f"desteklenmeyen ma_type: {ma_type}")

    n = len(df)
    long_stop = (mavg - multiplier * _atr).to_numpy(copy=True)
    short_stop = (mavg + multiplier * _atr).to_numpy(copy=True)
    m = mavg.to_numpy(copy=True)
    direction = np.ones(n, dtype=int)
    pmax_line = np.full(n, np.nan)

    for i in range(1, n):
        if np.isnan(long_stop[i]) or np.isnan(short_stop[i]):
            continue
        ls_prev = long_stop[i - 1] if not np.isnan(long_stop[i - 1]) else long_stop[i]
        ss_prev = short_stop[i - 1] if not np.isnan(short_stop[i - 1]) else short_stop[i]
        if m[i] > ls_prev:
            long_stop[i] = max(long_stop[i], ls_prev)
        if m[i] < ss_prev:
            short_stop[i] = min(short_stop[i], ss_prev)
        direction[i] = direction[i - 1]
        if direction[i] == -1 and m[i] > ss_prev:
            direction[i] = 1
        elif direction[i] == 1 and m[i] < ls_prev:
            direction[i] = -1
        pmax_line[i] = long_stop[i] if direction[i] == 1 else short_stop[i]

    return pd.DataFrame(
        {"pmax": pmax_line, "pmax_ma": mavg, "pmax_dir": direction}, index=df.index
    )


# ---------- 3) Nadaraya-Watson zarfı (yalnız endpoint / non-repaint) ----------

def nw_envelope(
    src: pd.Series, bandwidth: float = 8.0, window: int = 500, mult: float = 3.0
) -> pd.DataFrame:
    """Her barda yalnız GEÇMİŞ window bar kullanılır — endpoint yöntemi.

    Pine'daki repaint modunun sinyalleri backtest'te YASAK (docs/04 §R1); bu port
    o modu bilerek içermiyor.
    """
    i = np.arange(window, dtype=float)
    w = np.exp(-(i**2) / (2.0 * bandwidth * bandwidth))
    w_sum = w.sum()

    def _endpoint(x: np.ndarray) -> float:
        # x kronolojik gelir; en yeni bar en yüksek ağırlığı alır
        return float(np.dot(x[::-1], w) / w_sum)

    out = src.rolling(window).apply(_endpoint, raw=True)
    mae = (src - out).abs().rolling(window).mean() * mult
    return pd.DataFrame(
        {"nw_mid": out, "nw_upper": out + mae, "nw_lower": out - mae}, index=src.index
    )


# ---------- 4) Linreg kanalı (yalnız endpoint / non-repaint) ----------

def linreg_channel(
    src: pd.Series, length: int = 100, mult: float = 2.0
) -> pd.DataFrame:
    """Rolling pencere üzerinde OLS; her barın değeri o barda biten regresyonun ucu."""
    x = np.arange(length, dtype=float)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()

    def _fit(y: np.ndarray) -> float:
        slope = ((x - x_mean) * (y - y.mean())).sum() / x_var
        intercept = y.mean() - slope * x_mean
        return float(intercept + slope * (length - 1))

    endpoint = src.rolling(length).apply(_fit, raw=True)
    resid_std = src.rolling(length).apply(
        lambda y: float(
            np.std(y - (np.polyval(np.polyfit(x, y, 1), x)), ddof=0)
        ),
        raw=True,
    )
    return pd.DataFrame(
        {
            "lr_mid": endpoint,
            "lr_upper": endpoint + mult * resid_std,
            "lr_lower": endpoint - mult * resid_std,
        },
        index=src.index,
    )
