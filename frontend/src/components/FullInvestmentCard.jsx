import React from "react";
import { Card, CardBody } from "@heroui/react";
import StockGraph from "./StockGraph"; // Import the Chart.js graph
import UpArrow from "../assets/up-arrow.svg"; // Import Up Arrow
import DownArrow from "../assets/arrow-down.svg"; // Import Down Arrow

export default function FullInvestmentCard({ investmentAmount, changePercentage }) {
  const isPositive = changePercentage >= 0;
  const textColor = isPositive ? "text-green-500" : "text-red-700";
  const arrowIcon = isPositive ? UpArrow : DownArrow;

  // Navigate to /investment.html on click
  const handleCardClick = () => {
    window.location.href = "/investment.html"; // Redirect to investment page
  };

  return (
    <div onClick={handleCardClick} className="cursor-pointer w-fit">
      <Card
        isBlurred
        className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-700 dark:to-green-500 max-w-[800px] min-w-[800px] min-h-[400px] max-h-[400px] p-6 shadow-lg transition-transform transform hover:scale-105"
      >
        <CardBody>
          {/* Title - Matches Account Overview */}
          <div className="flex flex-col items-start">
            <h2 style={{ fontSize: "30px", fontWeight: "bold" }}>
              Your Portfolio
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
          <StockGraph height="h-56" />
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
