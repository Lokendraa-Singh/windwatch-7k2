import pandas as pd
import numpy as np

CUTOFF_HOUR = 9  # D-1 ko subah 9 baje tak ke forecast hi dekhenge

actual = pd.read_csv("actual_wind.csv", parse_dates=["startTime"])
fc = pd.read_csv("forecast_wind.csv", parse_dates=["startTime", "publishTime"])

# 1) Actual: duplicates hatao, sirf January rakho
actual = (actual.sort_values("publishTime")
                .drop_duplicates("startTime", keep="last"))
actual = actual[(actual.startTime >= "2026-01-01") & (actual.startTime < "2026-02-01")]
actual = actual[["startTime", "generation"]].rename(columns={"generation": "actual"})

# 2) Forecast: har startTime ke liye uska cutoff nikalo
fc["cutoff"] = (fc.startTime.dt.normalize()
                - pd.Timedelta(days=1)
                + pd.Timedelta(hours=CUTOFF_HOUR))

# sirf wo forecasts jo cutoff se pehle publish hue
fc = fc[fc.publishTime <= fc.cutoff]

# unmein se sabse naya publishTime
latest = (fc.sort_values("publishTime")
            .groupby("startTime", as_index=False)
            .last())
latest = latest[["startTime", "publishTime", "generation"]].rename(
    columns={"generation": "forecast"})
latest["horizon_h"] = (latest.startTime - latest.publishTime).dt.total_seconds() / 3600

# 3) Actual se join (hourly slots pe)
df = latest.merge(actual, on="startTime", how="inner")
df = df[(df.startTime >= "2026-01-01") & (df.startTime < "2026-02-01")]
df["error"] = df.forecast - df.actual
df["abs_error"] = df.error.abs()

# 4) Metrics
mae = df.abs_error.mean()
rmse = np.sqrt((df.error ** 2).mean())
bias = df.error.mean()
p95 = df.abs_error.quantile(0.95)
nz = df[df.actual > 0]
mape = (nz.abs_error / nz.actual).mean() * 100

print(f"Rows matched : {len(df)}")
print(f"MAE  : {mae:.0f} MW")
print(f"RMSE : {rmse:.0f} MW")
print(f"Bias : {bias:.0f} MW  (+ matlab forecast zyada, - matlab kam)")
print(f"P95 abs error: {p95:.0f} MW")
print(f"MAPE : {mape:.1f} %")
print(f"Horizon range: {df.horizon_h.min():.1f} - {df.horizon_h.max():.1f} hours")

df.to_csv("merged.csv", index=False)
print("\nSaved merged.csv")
print(df.head())