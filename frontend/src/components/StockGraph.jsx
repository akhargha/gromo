import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { date: "Jan", price: 120 },
  { date: "Feb", price: 135 },
  { date: "Mar", price: 110 },
  { date: "Apr", price: 140 },
  { date: "May", price: 125 },
  { date: "Jun", price: 150 },
];

export default function StockGraph() {
  return (
    <div className="w-full h-40 bg-gray-700 rounded-lg p-4 flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis dataKey="date" stroke="white" />
          <YAxis stroke="white" />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="#4CAF50" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
