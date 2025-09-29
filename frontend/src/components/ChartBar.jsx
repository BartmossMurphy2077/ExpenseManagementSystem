import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function ChartBar({ data }) {
  const chartData = {
    labels: data.map(d => d.title),
    datasets: [
      {
        label: "Amount",
        data: data.map(d => d.amount),
        backgroundColor: "rgba(75, 192, 192, 0.6)"
      }
    ]
  };
  return <Bar data={chartData} />;
}
