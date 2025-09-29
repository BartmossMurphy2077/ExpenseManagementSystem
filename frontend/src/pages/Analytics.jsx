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

  const dataPie = {
    labels: titles,
    datasets: [
      {
        data: amounts,
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0"],
      },
    ],
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Analytics</h2>
      <div style={{ width: "400px", marginBottom: "2rem" }}>
        <Bar data={dataBar} />
      </div>
      <div style={{ width: "300px" }}>
        <Pie data={dataPie} />
      </div>
    </div>
  );
}
