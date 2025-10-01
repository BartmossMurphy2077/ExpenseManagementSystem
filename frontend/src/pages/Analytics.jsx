// File: frontend/src/pages/Analytics.jsx
import { useEffect, useState } from "react";
import { api } from "../api";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function Analytics() {
  const [expenses, setExpenses] = useState([]);

  useEffect(() => {
    api.get("/expenses").then((res) => setExpenses(res.data || []));
  }, []);

  // Calculate monthly spending
  const monthlySpending = {};
  expenses.forEach(expense => {
    const date = new Date(expense.timestamp);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    monthlySpending[monthKey] = (monthlySpending[monthKey] || 0) + expense.amount;
  });

  const sortedMonths = Object.keys(monthlySpending).sort();
  const monthlyData = {
    labels: sortedMonths.map(month => {
      const [year, monthNum] = month.split('-');
      const date = new Date(year, monthNum - 1);
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    }),
    datasets: [{
      label: 'Monthly Spending',
      data: sortedMonths.map(month => monthlySpending[month]),
      backgroundColor: 'rgba(102, 126, 234, 0.8)',
      borderColor: 'rgba(102, 126, 234, 1)',
      borderWidth: 2,
      borderRadius: 6,
    }]
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        cornerRadius: 8,
        callbacks: {
          label: (context) => {
            const amount = new Intl.NumberFormat("en", {
              style: "currency",
              currency: "USD"
            }).format(context.parsed.y);
            return `Spent: ${amount}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      },
      x: {
        grid: {
          display: false,
        },
      }
    },
  };

  // Calculate tag sums and counts
  const tagSums = {};
  const tagCounts = {};

  expenses.forEach(expense => {
    const tags = expense.tags || [];
    tags.forEach(tag => {
      const tagName = typeof tag === "string" ? tag : tag?.name ?? "";
      if (tagName) {
        tagSums[tagName] = (tagSums[tagName] || 0) + expense.amount;
        tagCounts[tagName] = (tagCounts[tagName] || 0) + 1;
      }
    });
  });

  const tagLabels = Object.keys(tagSums);
  const tagData = tagLabels.map((l) => Math.round((tagSums[l] + Number.EPSILON) * 100) / 100);
  const totalTagAmount = tagData.reduce((s, v) => s + v, 0) || 1;
  const colors = tagLabels.map((_, i) => `hsl(${(i * 137.5) % 360} 65% 55%)`);

  const dataPie = {
    labels: tagLabels,
    datasets: [{
      data: tagData,
      backgroundColor: colors,
      borderColor: "rgba(255,255,255,0.8)",
      borderWidth: 2,
    }],
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right",
        labels: {
          padding: 20,
          font: {
            size: 12,
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        cornerRadius: 8,
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
  };

  // Styles
  const container = {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    padding: "2rem",
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
  };

  const card = {
    width: "100%",
    maxWidth: "1200px",
    background: "#ffffff",
    borderRadius: "16px",
    boxShadow: "0 20px 40px rgba(0, 0, 0, 0.1)",
    overflow: "hidden",
    marginTop: "2rem",
  };

  const header = {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    padding: "2rem",
    textAlign: "center",
  };

  const title = {
    fontSize: "2rem",
    fontWeight: "700",
    margin: "0 0 0.5rem 0",
    letterSpacing: "-0.025em",
  };

  const subtitle = {
    fontSize: "1rem",
    opacity: "0.9",
    margin: "0",
    fontWeight: "400",
  };

  const content = {
    padding: "2rem",
  };

  const grid = {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "2rem",
    marginBottom: "2rem",
  };

  const chartContainer = {
    background: "#f8fafc",
    borderRadius: "12px",
    padding: "1.5rem",
    border: "1px solid #e2e8f0",
  };

  const chartTitle = {
    fontSize: "1.25rem",
    fontWeight: "600",
    color: "#1e293b",
    margin: "0 0 1.5rem 0",
  };

  const chartBox = {
    height: "300px",
    position: "relative",
  };

  const statsContainer = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "1rem",
    marginTop: "2rem",
  };

  const statCard = {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    padding: "1.5rem",
    borderRadius: "12px",
    textAlign: "center",
  };

  const statValue = {
    fontSize: "2rem",
    fontWeight: "700",
    margin: "0 0 0.5rem 0",
  };

  const statLabel = {
    fontSize: "0.875rem",
    opacity: "0.9",
    margin: "0",
  };

  const totalExpenses = expenses.length;
  const totalAmount = expenses.reduce((sum, exp) => sum + exp.amount, 0);
  const averageExpense = totalExpenses > 0 ? totalAmount / totalExpenses : 0;

  return (
    <div style={container}>
      <div style={card}>
        <div style={header}>
          <h1 style={title}>Analytics Dashboard</h1>
          <p style={subtitle}>Comprehensive overview of your spending patterns</p>
        </div>

        <div style={content}>
          <div style={grid}>
            <div style={chartContainer}>
              <h3 style={chartTitle}>Monthly Spending Trends</h3>
              <div style={chartBox}>
                <Bar data={monthlyData} options={barOptions} />
              </div>
            </div>

            <div style={chartContainer}>
              <h3 style={chartTitle}>Spending by Category</h3>
              <div style={chartBox}>
                <Pie data={dataPie} options={pieOptions} />
              </div>
            </div>
          </div>

          <div style={statsContainer}>
            <div style={statCard}>
              <div style={statValue}>{totalExpenses}</div>
              <div style={statLabel}>Total Expenses</div>
            </div>
            <div style={statCard}>
              <div style={statValue}>
                ${totalAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div style={statLabel}>Total Spent</div>
            </div>
            <div style={statCard}>
              <div style={statValue}>
                ${averageExpense.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div style={statLabel}>Average Expense</div>
            </div>
            <div style={statCard}>
              <div style={statValue}>{tagLabels.length}</div>
              <div style={statLabel}>Categories Used</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
