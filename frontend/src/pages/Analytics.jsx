// File: frontend/src/pages/Analytics.jsx
import { useEffect, useState } from "react";
import { api } from "../api";
import { Pie } from "react-chartjs-2";
import ChartBar from "../components/ChartBar";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function Analytics() {
  const [expenses, setExpenses] = useState([]);

  useEffect(() => {
    api.get("/expenses").then((res) => setExpenses(res.data || []));
  }, []);

  const tagLabels = Object.keys(tagSums);
  const tagData = tagLabels.map((l) => Math.round((tagSums[l] + Number.EPSILON) * 100) / 100);
  const totalTagAmount = tagData.reduce((s, v) => s + v, 0) || 1;
  const colors = tagLabels.map((_, i) => `hsl(${(i * 137.5) % 360} 65% 55% / 0.9)`);

  const dataPie = {
    labels: tagLabels,
    datasets: [{ data: tagData, backgroundColor: colors, borderColor: "rgba(255,255,255,0.6)", borderWidth: 1 }],
  };

  const pieOptions = {
    plugins: {
      legend: { position: "right" },
      tooltip: {
        callbacks: {
          label: (context) => {
            const idx = context.dataIndex;
            const label = tagLabels[idx] ?? "";
            const amount = tagData[idx] ?? 0;
            const pct = ((amount / totalTagAmount) * 100).toFixed(1);
            const count = tagCounts[label] ?? 0;
            const money = new Intl.NumberFormat("en", { style: "currency", currency: "USD" }).format(amount);
            return `${label}: ${money} (${pct}%) — ${count} ${count === 1 ? "item" : "items"}`;
          },
        },
      },
    },
    maintainAspectRatio: false,
  };

  // Styles (same as before)
  const container = { /* ... */ };
  const card = { /* ... */ };
  const header = { /* ... */ };
  const grid = { /* ... */ };
  const chartBox = { /* ... */ };
  const pieBox = { /* ... */ };
  const totalBadge = { /* ... */ };

  return (
    <div style={container}>
      <div style={card}>
        <div style={header}>
          <h2 style={{ margin: 0 }}>Analytics</h2>
          <div>Overview of spending by month and tag</div>
        </div>

        <div style={grid}>
          <div style={chartBox}>
            <h3 style={{ marginTop: 0 }}>Monthly Spending</h3>
            {/* Use ChartBar here */}
            <ChartBar data={expenses} />
          </div>

          <div style={pieBox}>
            <div style={{ marginBottom: "0.5rem" }}>
              <h3 style={{ margin: 0 }}>Tag proportions (by money)</h3>
            </div>
            <div style={{ flex: 1, minHeight: 220 }}>
              <Pie data={dataPie} options={pieOptions} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
