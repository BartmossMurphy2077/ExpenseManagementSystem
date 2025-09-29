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
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    map[key] = (map[key] || 0) + Number(e.amount || 0);
    return map;
  }, {});

  const monthKeys = Object.keys(monthlyMap).sort();
  const monthLabels = monthKeys.map((k) => {
    const [y, m] = k.split("-");
    const dt = new Date(Number(y), Number(m) - 1, 1);
    return new Intl.DateTimeFormat("en", { year: "numeric", month: "short" }).format(dt);
  });
  const monthData = monthKeys.map((k) => Math.round((monthlyMap[k] + Number.EPSILON) * 100) / 100);

  const dataBar = {
    labels: monthLabels,
    datasets: [
      {
        label: "Monthly Spending",
        data: monthData,
        backgroundColor: "rgba(75, 192, 192, 0.8)",
        borderRadius: 6,
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
            return ` ${new Intl.NumberFormat("en", { style: "currency", currency: "USD" }).format(val)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { callback: (v) => `$${v}` },
        title: { display: true, text: "Amount" },
      },
      x: { title: { display: true, text: "Month" } },
    },
  };

  // Total expenditure
  const totalExpenditure = expenses.reduce((s, e) => s + Number(e.amount || 0), 0);
  const formattedTotal = new Intl.NumberFormat("en", { style: "currency", currency: "USD" }).format(totalExpenditure);

  // Tag sums (money per tag) and counts
  const tagSums = expenses.reduce((acc, e) => {
    (e.tags || []).forEach((t) => {
      const name = typeof t === "string" ? t : t?.name ?? "";
      if (!name) return;
      acc[name] = (acc[name] || 0) + Number(e.amount || 0);
    });
    return acc;
  }, {});
  const tagCounts = expenses.reduce((acc, e) => {
    (e.tags || []).forEach((t) => {
      const name = typeof t === "string" ? t : t?.name ?? "";
      if (!name) return;
      acc[name] = (acc[name] || 0) + 1;
    });
    return acc;
  }, {});

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

  // Styles
  const container = {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "2rem",
    background: "linear-gradient(180deg, #f6fbff 0%, #ffffff 100%)",
  };

  const card = {
    width: "100%",
    maxWidth: 1100,
    background: "#fff",
    borderRadius: 12,
    boxShadow: "0 8px 24px rgba(15, 23, 42, 0.08)",
    padding: "1.25rem 1.5rem",
    boxSizing: "border-box",
  };

  const header = { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" };
  const title = { margin: 0, fontSize: "1.25rem", color: "#0f172a" };
  const subtitle = { color: "#64748b", fontSize: "0.95rem" };

  const grid = {
    display: "grid",
    gridTemplateColumns: "1fr",
    gap: "1.25rem",
  };

  // make two-column layout on wider screens
  const mediaQuery = typeof window !== "undefined" && window.matchMedia && window.matchMedia("(min-width: 880px)").matches;
  if (mediaQuery) {
    grid.gridTemplateColumns = "1fr 420px";
  }

  const chartBox = { background: "#fbfdff", padding: "1rem", borderRadius: 10, minHeight: 220 };
  const pieBox = { background: "#fbfdff", padding: "1rem", borderRadius: 10, minHeight: 320, display: "flex", flexDirection: "column" };
  const totalBadge = { marginBottom: "0.5rem", fontSize: "1.05rem", fontWeight: 700, color: "#064e3b" };

  return (
    <div style={container}>
      <div style={card}>
        <div style={header}>
          <div>
            <h2 style={title}>Analytics</h2>
            <div style={subtitle}>Overview of spending by month and tag</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: "0.9rem", color: "#0f172a", fontWeight: 600 }}>Total</div>
            <div style={{ fontSize: "1rem", color: "#0f172a" }}>{formattedTotal}</div>
          </div>
        </div>

        <div style={grid}>
          <div style={chartBox}>
            <h3 style={{ marginTop: 0, marginBottom: "0.6rem", fontSize: "1rem" }}>Monthly Spending</h3>
            <Bar data={dataBar} options={barOptions} />
          </div>

          <div style={pieBox}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
              <h3 style={{ margin: 0, fontSize: "1rem" }}>Tag proportions (by money)</h3>
              <div style={{ fontSize: "0.9rem", color: "#475569" }}>{new Intl.NumberFormat("en", { style: "currency", currency: "USD" }).format(totalTagAmount)}</div>
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
