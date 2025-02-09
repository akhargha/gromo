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

// Updated API endpoint to match your backend service
const INVESTMENT_URL = "http://localhost:8001/investment_chart";

export default function StockGraph({ height = "h-40", sampleInterval = 1 }) {
  const [investmentData, setInvestmentData] = useState([]);

  useEffect(() => {
    // Fetch the portfolio data from the backend
    fetch(INVESTMENT_URL)
      .then((response) => response.json())
      .then((data) => {
        // Since the API returns an array, set the state directly
        setInvestmentData(data);
      })
      .catch((error) =>
        console.error("Error fetching investment data:", error)
      );
  }, []);

  // Optionally downsample the data based on sampleInterval
  const filteredData =
    sampleInterval > 1
      ? investmentData.filter((_, index) => index % sampleInterval === 0)
      : investmentData;

  // Format date labels from the "week" field
  const formatDate = (dateStr) => {
    const options = { month: "short", day: "numeric" };
    return new Date(dateStr).toLocaleDateString("en-US", options);
  };

  // Extract labels (dates from the week field) and data points (portfolio value)
  const labels = filteredData.map((point) => formatDate(point.week));
  const dataPoints = filteredData.map((point) => point.portfolio_value);

  // Define the dataset for the line chart
  const data = {
    labels,
    datasets: [
      {
        label: "Portfolio Value ($)",
        data: dataPoints,
        segment: {
          borderColor: (ctx) =>
            ctx.p1.parsed.y < ctx.p0.parsed.y ? "red" : "green",
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
