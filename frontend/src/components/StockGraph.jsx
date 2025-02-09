import React from "react";
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

export default function StockGraph({ height = "h-40" }) { // Default height is h-40, can be overridden
  const data = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    datasets: [
      {
        label: "Investment Value ($)",
        data: [120, 135, 110, 140, 125, 150], // Sample data
        // Remove static borderColor and add a segment configuration instead.
        segment: {
          borderColor: (ctx) =>
            ctx.p1.parsed.y < ctx.p0.parsed.y ? "red" : "green",
        },
        backgroundColor: "rgba(76, 175, 80, 0.2)", // Slight green fill remains unchanged
        tension: 0.1, // Smooth curves
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: "darkgreen",
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false, // Allows the graph to adapt to container size
    plugins: {
      legend: { display: false }, // Hide legend for a cleaner look
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
