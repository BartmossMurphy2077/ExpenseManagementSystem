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

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function Analytics() {
  const [expenses, setExpenses] = useState([]);

  useEffect(() => {
    api.get("/expenses").then((res) => setExpenses(res.data || []));
  }, []);

  // Helper: safe parse of various timestamp fields
  const parseDate = (expense) => {
    const raw = expense.timestamp ?? expense.created_at ?? expense.createdAt ?? expense.date ?? null;
    if (!raw) return null;
    const d = raw instanceof Date ? raw : new Date(raw);
    return isNaN(d.getTime()) ? null : d;
  };

  // Group expenses by month (YYYY-MM) and sum amounts
  const monthlyMap = expenses.reduce((map, e) => {
    const d = parseDate(e);
    if (!d) return map;
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`; // YYYY-MM
    map[key] = (map[key] || 0) + Number(e.amount || 0);
    return map;
  }, {});

  // Sort month keys ascending and build labels & data
  const monthKeys = Object.keys(monthlyMap).sort();
  const monthLabels = monthKeys.map((k) => {
    const [y, m] = k.split("-");
    const dt = new Date(Number(y), Number(m) - 1, 1);
    return new Intl.DateTimeFormat("en", { year: "numeric", month: "short" }).format(dt); // e.g. "Sep 2025"
  });
  const monthData = monthKeys.map((k) => Math.round((monthlyMap[k] + Number.EPSILON) * 100) / 100);

  const dataBar = {
    labels: monthLabels,
    datasets: [
      {
        label: "Monthly Spending",
        data: monthData,
        backgroundColor: "rgba(75, 192, 192, 0.6)",
      },
    ],
  };

  const barOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const val = ctx.parsed.y ?? ctx.parsed ?? 0;
            return ` $${new Intl.NumberFormat("en", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (v) => `$${v}`,
        },
        title: { display: true, text: "Amount" },
      },
      x: { title: { display: true, text: "Month" } },
    },
  };

  // Total expenditure across all expenses
  const totalExpenditure = expenses.reduce((s, e) => s + Number(e.amount || 0), 0);
  const formattedTotal = new Intl.NumberFormat("en", { style: "currency", currency: "USD" }).format(totalExpenditure);

  // Tag proportions (unchanged logic, handles strings or objects)
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
  const colors = tagLabels.map((_, i) => `hsl(${(i * 137.5) % 360} 65% 55% / 0.9)`);

  const dataPie = {
    labels: tagLabels,
    datasets: [{ data: tagData, backgroundColor: colors }],
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

      <div style={{ width: "100%", maxWidth: 800, marginBottom: "2rem" }}>
        <h3>Monthly Spending</h3>
        <Bar data={dataBar} options={barOptions} />
      </div>

      <div style={{ width: "100%", maxWidth: 800 }}>
        <h3>Tag proportions</h3>
        <div style={{ marginBottom: "0.5rem", fontSize: "1.1rem", fontWeight: 600 }}>
          Total expenditure: {formattedTotal}
        </div>
        <div style={{ width: "100%", maxWidth: 400, height: 360 }}>
          <Pie data={dataPie} options={pieOptions} />
        </div>
      </div>
    </div>
  );
}
