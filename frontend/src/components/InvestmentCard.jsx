import React from "react";
import { Card, CardBody } from "@heroui/react";
import StockGraph from "./StockGraph"; // Import the Chart.js graph
import UpArrow from "../assets/up-arrow.svg"; // Import Up Arrow
import DownArrow from "../assets/arrow-down.svg"; // Import Down Arrow

export default function InvestmentCard({ investmentAmount, changePercentage, onClick }) {
  const isPositive = changePercentage >= 0;
  const textColor = isPositive ? "text-green-500" : "text-red-700";
  const arrowIcon = isPositive ? UpArrow : DownArrow; // Choose correct arrow

  return (
    <Card
      isBlurred
      onClick={onClick}
      className="cursor-pointer border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-700 dark:to-green-500 max-w-[400px] min-h-[329px] max-h-[329px] p-6 shadow-lg transition-transform transform hover:scale-105"
    >
      <CardBody>
        {/* Title - Matches Account Overview */}
        <div className="flex flex-col items-start">
        <h2
            style={{
              fontFamily: "sans-serif",
              color: "white",
              textShadow:
                "1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000",
              fontSize: "30px",
            }}
          >
            Your Investments
          </h2>

          {/* Investment Amount & Percentage with Arrow */}
          <div className="flex items-center gap-1 mt-1">
            <p className="text-lg text-white/80">${investmentAmount}</p>
            <p className={`text-lg ${textColor} flex items-center`}>
              ({changePercentage}%)
              <img src={arrowIcon} alt="change direction" className="w-4 h-4 ml-1" />
            </p>
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
