import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, BarChart, Bar,
} from "recharts";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function Card({ title, value, unit }) {
  return (
    <div style={{ background: "#f4f6f8", borderRadius: 8, padding: 16, minWidth: 140 }}>
      <div style={{ fontSize: 12, color: "#555" }}>{title}</div>
      <div style={{ fontSize: 24, fontWeight: 600 }}>
        {value ?? "-"} <span style={{ fontSize: 12 }}>{unit}</span>
      </div>
    </div>
  );
}

export default function App() {
  const [dates, setDates] = useState([]);
  const [date, setDate] = useState("2026-01-12");
  const [day, setDay] = useState(null);
  const [overall, setOverall] = useState(null);
  const [buckets, setBuckets] = useState([]);

  useEffect(() => {
    fetch(`${API}/api/dates`).then(r => r.json()).then(setDates);
    fetch(`${API}/api/metrics`).then(r => r.json()).then(setOverall);
    fetch(`${API}/api/buckets`).then(r => r.json()).then(setBuckets);
  }, []);

  useEffect(() => {
    fetch(`${API}/api/forecast?date=${date}`).then(r => r.json()).then(setDay);
  }, [date]);

  const points = day?.points.map(p => ({ ...p, hour: p.startTime.slice(11, 16) })) ?? [];

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: 24, fontFamily: "sans-serif" }}>
      <h1>Wind Forecast Accuracy: January 2026</h1>
      <p style={{ color: "#555" }}>
        Forecast = latest version published before 09:00 UTC on the day before delivery.
      </p>

      <h3>January overall</h3>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <Card title="MAE" value={overall?.mae} unit="MW" />
        <Card title="RMSE" value={overall?.rmse} unit="MW" />
        <Card title="Bias (+ = over-forecast)" value={overall?.bias} unit="MW" />
        <Card title="P95 abs error" value={overall?.p95_abs_error} unit="MW" />
        <Card title="MAPE" value={overall?.mape_pct} unit="%" />
      </div>

      <h3 style={{ marginTop: 32 }}>Forecast vs actual</h3>
      <select value={date} onChange={e => setDate(e.target.value)}>
        {dates.map(d => <option key={d} value={d}>{d}</option>)}
      </select>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", margin: "12px 0" }}>
        <Card title="Day MAE" value={day?.metrics.mae} unit="MW" />
        <Card title="Day bias" value={day?.metrics.bias} unit="MW" />
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={points}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="hour" />
          <YAxis unit=" MW" width={80} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="forecast" stroke="#2563eb" dot={false} />
          <Line type="monotone" dataKey="actual" stroke="#16a34a" dot={false} />
        </LineChart>
      </ResponsiveContainer>

      <h3 style={{ marginTop: 32 }}>Error by forecast level</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={buckets}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="bucket" />
          <YAxis unit=" MW" width={80} />
          <Tooltip />
          <Legend />
          <Bar dataKey="mae" fill="#f59e0b" name="MAE" />
          <Bar dataKey="bias" fill="#dc2626" name="Bias" />
          <Bar dataKey="p95_abs_error" fill="#6b7280" name="P95 error" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}