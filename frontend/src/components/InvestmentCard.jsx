import React from "react";
import { Card, CardBody } from "@heroui/react";
import StockGraph from "./StockGraph"; // Import the Chart.js graph

export default function InvestmentCard({ investmentAmount, changePercentage, onClick }) {
  const textColor = changePercentage >= 0 ? "text-green-500" : "text-red-500";

  return (
    <Card
      isBlurred
      onClick={onClick}
      className="cursor-pointer border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-700 dark:to-green-500 max-w-[400px] min-h-[329px] max-h-[329px] p-6 shadow-lg transition-transform transform hover:scale-105"
    >
      <CardBody>
        {/* Title - Matches Account Overview */}
        <div className="flex flex-col items-start">
          <h2 className="text-2xl font-bold text-white">Your Investments</h2>

          {/* Investment Amount & Percentage on the Same Line */}
          <div className="flex items-center gap-0.5">
            <p className="text-lg text-white/80">${investmentAmount}</p>
            <p className={`text-lg ${textColor}`}>({changePercentage}%)</p>
          </div>
        </div>

        {/* Stock Graph using Chart.js */}
        <div className="mt-6">
          <StockGraph />
        </div>
      </CardBody>
    </Card>
  );
}
