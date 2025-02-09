import React, { useEffect, useState } from "react";
import { Card, CardBody } from "@heroui/react";
import StockGraph from "./StockGraph"; // Import the Chart.js graph
import UpArrow from "../assets/up-arrow.svg"; // Import Up Arrow
import DownArrow from "../assets/arrow-down.svg"; // Import Down Arrow

const INVESTMENT_URL = "http://127.0.0.1:5000/api/investment/4"; // API endpoint

export default function FullInvestmentCard() {
  const [investmentAmount, setInvestmentAmount] = useState(null);
  const [changePercentage, setChangePercentage] = useState(null);

  useEffect(() => {
    fetch(INVESTMENT_URL)
      .then((response) => response.json())
      .then((data) => {
        if (data.investment_history && data.investment_history.length > 0) {
          const firstInvestment = data.investment_history[0].y; // First row y value
          const lastInvestment = data.investment_history[data.investment_history.length - 1].y; // Last row y value

          setInvestmentAmount(lastInvestment.toFixed(2)); // Set last investment value
          const percentChange = ((lastInvestment - firstInvestment) / firstInvestment) * 100; // Change percentage formula
          setChangePercentage(percentChange.toFixed(2)); // Set percent change
        }
      })
      .catch((error) => console.error("Error fetching investment data:", error));
  }, []);

  const isPositive = changePercentage >= 0;
  const textColor = isPositive ? "text-green-500" : "text-red-700";
  const arrowIcon = isPositive ? UpArrow : DownArrow;

  return (
    <div className="w-fit">
      <Card
        isBlurred
        className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-700 dark:to-green-500 max-w-[800px] min-w-[800px] min-h-[400px] max-h-[400px] p-6 shadow-lg transition-transform transform"
      >
        <CardBody>
          {/* Title - Matches Account Overview */}
          <div className="flex flex-col items-start">
            <h2 style={{ fontSize: "30px", fontWeight: "bold" }}>
              Your Portfolio
            </h2>

            {/* Investment Amount & Percentage with Arrow */}
            <div className="flex items-center gap-1 mt-1">
              <p className="text-lg text-white/80">
                ${investmentAmount !== null ? investmentAmount : "Loading..."}
              </p>
              {changePercentage !== null && (
                <p className={`text-lg ${textColor} flex items-center`}>
                  ({changePercentage}%)
                  <img src={arrowIcon} alt="change direction" className="w-4 h-4 ml-1" />
                </p>
              )}
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
