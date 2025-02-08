import React from "react";
import { Card, CardBody } from "@heroui/react";
import StockGraph from "./StockGraph";

export default function InvestmentCard({ investmentAmount, changePercentage, onClick }) {
  // Determine text color based on percentage change
  const textColor = changePercentage >= 0 ? "text-green-500" : "text-red-500";

  return (
    <Card
      isBlurred
      onClick={onClick} // Makes the entire card clickable
      className="cursor-pointer border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-700 dark:to-green-500 max-w-[400px] p-6 shadow-lg min-h-[328px] transition-transform transform hover:scale-105"
    >
      <CardBody>
        {/* Title */}
        <div className="flex flex-col items-start">
          <h2 className="text-2xl font-bold text-white">Your Investments</h2>
        </div>

        {/* Investment Details */}
        <div className="flex flex-col mt-1">
          <p className="text-l font-medium text-gray-200">
            ${investmentAmount}<span className={`ml-1 ${textColor}`}>({changePercentage}%)</span>
          </p>
        </div>

        {/* Graph Placeholder */}
        <StockGraph />
      </CardBody>
    </Card>
  );
}
