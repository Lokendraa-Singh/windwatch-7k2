# Wind Forecast Accuracy Dashboard

Dashboard for a UK utility's day-ahead desk: shows the latest wind forecast
available at decision time and quantifies its accuracy (January 2026).

**Live app:** https://windwatch-7k2.vercel.app
**API docs:** https://windwatch-7k2.onrender.com/docs
(Render free tier sleeps; first request can take about a minute.)

## Method
- Actuals: Elexon FUELHH, fuelType = WIND. Forecasts: Elexon WINDFOR.
- For each target hour, the forecast used is the latest publishTime up to
  09:00 UTC on the day before delivery (assumed day-ahead cutoff, editable
  in analyse.py).
- Forecast is hourly, so comparison is on hourly slots.
- Metrics: MAE, RMSE, bias (forecast - actual), P95 absolute error, MAPE.
- Errors are also split by forecast level (low / mid / high wind).

## Files
- `fetch_data.py`: downloads actual and forecast data from Elexon
- `analyse.py`: picks latest forecast before cutoff, joins with actuals, computes errors, writes merged.csv
- `check.py`: sanity checks on the merged data
- `backend/`: FastAPI app (main.py), data/merged.csv, Dockerfile, requirements.txt
- `frontend/`: React (Vite) + Recharts, Dockerfile
- `docker-compose.yml`: runs both services together

## Run locally
With Docker:

    docker compose up --build

Open http://localhost:3000

Without Docker:

    cd backend
    pip install -r requirements.txt
    python -m uvicorn main:app --reload

    cd frontend
    npm install
    npm run dev

Open http://localhost:5173

## Limitations
- Only one month of data. The cutoff time is an assumption. No demand data.

## AI usage
AI tools (Claude) were used to assist with writing code and documentation.