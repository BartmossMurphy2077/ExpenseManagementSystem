// javascript
import { useEffect, useState } from "react";
import { api } from "../api";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

// Register chart.js components ONCE, at the top
ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function Analytics() {
  const [expenses, setExpenses] = useState([]);

  useEffect(() => {
    api.get("/expenses").then((res) => setExpenses(res.data));
  }, []);

  const amounts = expenses.map((e) => e.amount);
  const titles = expenses.map((e) => e.title);

  const dataBar = {
    labels: titles,
    datasets: [
      {
        label: "Amount",
        data: amounts,
        backgroundColor: "rgba(75, 192, 192, 0.6)",
      },
    ],
  };

  // Compute tag counts (handles tags as strings or objects with `name`)
  const tagCounts = expenses.reduce((acc, e) => {
    (e.tags || []).forEach((t) => {
      const name = typeof t === "string" ? t : t?.name ?? "";
      if (!name) return;
      acc[name] = (acc[name] || 0) + 1;
    });
    return acc;
  }, {});

  const tagLabels = Object.keys(tagCounts);
  const tagData = tagLabels.map((l) => tagCounts[l]);
  const totalTags = tagData.reduce((s, v) => s + v, 0) || 1;

  // generate colors
  const colors = tagLabels.map((_, i) => `hsl(${(i * 137.5) % 360} 65% 55% / 0.9)`);

  const dataPie = {
    labels: tagLabels,
    datasets: [
      {
        data: tagData,
        backgroundColor: colors,
      },
    ],
  };

  const pieOptions = {
    plugins: {
      legend: { position: "right" },
      tooltip: {
        callbacks: {
          label: (context) => {
            const idx = context.dataIndex;
            const label = tagLabels[idx] ?? "";
            const count = tagData[idx] ?? 0;
            const pct = ((count / totalTags) * 100).toFixed(1);
            return `${label}: ${count} (${pct}%)`;
          },
        },
      },
    },
    maintainAspectRatio: false,
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Analytics</h2>
      <div style={{ width: "400px", marginBottom: "2rem" }}>
        <Bar data={dataBar} />
      </div>
      <div style={{ width: "400px", height: "360px" }}>
        <h3>Tag proportions</h3>
        <Pie data={dataPie} options={pieOptions} />
      </div>
    </div>
  );
}
