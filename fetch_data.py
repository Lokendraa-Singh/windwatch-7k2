import requests
import pandas as pd
from datetime import datetime, timedelta

BASE = "https://data.elexon.co.uk/bmrs/api/v1/datasets"


def fetch_range(dataset, start, end, extra_params=None, chunk_days=7):
    """Date range ko chhote tukdon mein todke data laata hai."""
    rows = []
    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=chunk_days), end)
        params = {
            "publishDateTimeFrom": cur.strftime("%Y-%m-%dT%H:%MZ"),
            "publishDateTimeTo": nxt.strftime("%Y-%m-%dT%H:%MZ"),
            "format": "json",
        }
        if extra_params:
            params.update(extra_params)
        r = requests.get(f"{BASE}/{dataset}/stream", params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        print(f"{dataset}: {cur.date()} -> {nxt.date()} : {len(data)} rows")
        rows.extend(data)
        cur = nxt
    return pd.DataFrame(rows)


# 1) ACTUAL wind generation (January 2026)
actual = fetch_range(
    "FUELHH",
    datetime(2026, 1, 1),
    datetime(2026, 2, 1),
    extra_params={"fuelType": "WIND"},
)
actual = actual[actual["fuelType"] == "WIND"]
actual.to_csv("actual_wind.csv", index=False)

# 2) FORECAST wind generation
# Dec ke end se lete hain, kyunki 1 Jan ke decision ke liye purane forecasts bhi chahiye
forecast = fetch_range(
    "WINDFOR",
    datetime(2025, 12, 25),
    datetime(2026, 2, 1),
)
forecast.to_csv("forecast_wind.csv", index=False)

print("\nActual columns:", list(actual.columns))
print(actual.head())
print("\nForecast columns:", list(forecast.columns))
print(forecast.head())