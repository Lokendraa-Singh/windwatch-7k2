from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Wind Forecast Accuracy API")

# React frontend ko is API se baat karne do
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).parent / "data" / "merged.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["startTime", "publishTime"])
df["date"] = df.startTime.dt.strftime("%Y-%m-%d")


def compute_metrics(d: pd.DataFrame) -> dict:
    if d.empty:
        return {}
    nz = d[d.actual > 0]
    return {
        "rows": int(len(d)),
        "mae": round(float(d.abs_error.mean()), 1),
        "rmse": round(float(np.sqrt((d.error ** 2).mean())), 1),
        "bias": round(float(d.error.mean()), 1),
        "p95_abs_error": round(float(d.abs_error.quantile(0.95)), 1),
        "mape_pct": round(float((nz.abs_error / nz.actual).mean() * 100), 1),
    }

@app.get("/")
def root():
    return {"service": "Wind Forecast Accuracy API", "docs": "/docs", "metrics": "/api/metrics"}

@app.get("/api/health")
def health():
    return {"status": "ok", "rows": len(df)}


@app.get("/api/dates")
def dates():
    """Dropdown ke liye available delivery dates."""
    return sorted(df.date.unique().tolist())


@app.get("/api/forecast")
def forecast(date: str):
    """Ek din ka forecast vs actual (ghante ke hisaab se)."""
    day = df[df.date == date]
    if day.empty:
        raise HTTPException(404, f"No data for {date}")
    out = day[["startTime", "publishTime", "forecast", "actual",
               "error", "horizon_h"]].copy()
    out["startTime"] = out.startTime.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out["publishTime"] = out.publishTime.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "date": date,
        "metrics": compute_metrics(day),
        "points": out.to_dict(orient="records"),
    }


@app.get("/api/metrics")
def metrics(date_from: str | None = None, date_to: str | None = None):
    """Poore January (ya chune hue range) ke metrics."""
    d = df
    if date_from:
        d = d[d.date >= date_from]
    if date_to:
        d = d[d.date <= date_to]
    return compute_metrics(d)


@app.get("/api/daily")
def daily():
    """Har din ka MAE aur bias (best/worst din dikhane ke liye)."""
    g = df.groupby("date").agg(
        forecast=("forecast", "mean"),
        actual=("actual", "mean"),
        mae=("abs_error", "mean"),
        bias=("error", "mean"),
    ).round(0).reset_index()
    return g.to_dict(orient="records")


@app.get("/api/buckets")
def buckets():
    """Forecast ke level ke hisaab se error (low/mid/high wind)."""
    bins = [0, 10000, 15000, float("inf")]
    labels = ["Low (<10 GW)", "Mid (10-15 GW)", "High (>15 GW)"]
    d = df.copy()
    d["bucket"] = pd.cut(d.forecast, bins=bins, labels=labels, right=False)
    out = []
    for label in labels:
        part = d[d.bucket == label]
        m = compute_metrics(part)
        if m:
            out.append({"bucket": label, **m})
    return out