import pandas as pd

df = pd.read_csv("merged.csv", parse_dates=["startTime", "publishTime"])

print(df[["startTime", "forecast", "actual", "error"]].head(12))
print("\nForecast average:", round(df.forecast.mean()), "MW")
print("Actual average  :", round(df.actual.mean()), "MW")

df["day"] = df.startTime.dt.date
daily = df.groupby("day").agg(forecast=("forecast", "mean"),
                             actual=("actual", "mean"),
                              bias=("error", "mean")).round(0)
print("\nDin ke hisaab se:")
print(daily)