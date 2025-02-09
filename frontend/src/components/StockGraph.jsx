import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";

// Register required components
ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const INVESTMENT_URL = "http://127.0.0.1:5000/api/investment/4"; // API endpoint

export default function StockGraph({ height = "h-40" }) {
  const [investmentData, setInvestmentData] = useState([]);

  useEffect(() => {
    // Fetch investment history
    fetch(INVESTMENT_URL)
      .then((response) => response.json())
      .then((data) => {
        if (data.investment_history) {
          setInvestmentData(data.investment_history);
        }
      })
      .catch((error) => console.error("Error fetching investment data:", error));
  }, []);

  // Format date labels
  const formatDate = (dateStr) => {
    const options = { month: "short", day: "numeric" };
    return new Date(dateStr).toLocaleDateString("en-US", options);
  };

  // Extract labels (dates) and data points (investment values)
  const labels = investmentData.map((point) => formatDate(point.x));
  const dataPoints = investmentData.map((point) => point.y);

  // Define dataset
  const data = {
    labels,
    datasets: [
      {
        label: "Investment Value ($)",
        data: dataPoints,
        segment: {
          borderColor: (ctx) =>
            ctx.p1.parsed.y < ctx.p0.parsed.y ? "red" : "green", // Red for downward trend, green for upward
        },
        backgroundColor: "rgba(76, 175, 80, 0.2)", // Slight green fill
        tension: 0.1, // Smooth curves
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: "darkgreen",
        fill: true,
      },
    ],
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: true },
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: "white" } },
      y: { grid: { display: true }, ticks: { color: "white" } },
    },
  };

  return (
    <div className={`w-full ${height} bg-black rounded-lg p-4 shadow-md`}>
      <Line data={data} options={options} />
    </div>
  );
}
