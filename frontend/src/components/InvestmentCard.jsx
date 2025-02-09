import React, { useState, useEffect } from "react";
import { Card, CardBody } from "@heroui/react";
import StockGraph from "./StockGraph"; // Import Chart.js graph
import UpArrow from "../assets/up-arrow.svg"; // Import Up Arrow
import DownArrow from "../assets/arrow-down.svg"; // Import Down Arrow

const INVESTMENT_URL = "http://127.0.0.1:5000/api/investment/4"; // API endpoint

export default function InvestmentCard() {
  const [investmentAmount, setInvestmentAmount] = useState(null);
  const [changePercentage, setChangePercentage] = useState(null);

  useEffect(() => {
    const fetchInvestmentData = async () => {
      try {
        const response = await fetch(INVESTMENT_URL);
        const data = await response.json();
        if (data?.investment_history?.length > 0) {
          const { investment_history } = data;
          const firstY = investment_history[0].y;
          const lastY = investment_history[investment_history.length - 1].y;
          setInvestmentAmount(lastY.toFixed(2));
          const change = ((lastY - firstY) / firstY) * 100;
          setChangePercentage(change.toFixed(2));
        }
      } catch (error) {
        console.error("Error fetching investment data:", error);
      }
    };
    fetchInvestmentData();
  }, []);

  const isPositive = Number(changePercentage) >= 0;
  const textColor = isPositive ? "text-green-500" : "text-red-700";
  const arrowIcon = isPositive ? UpArrow : DownArrow;

  const handleCardClick = () => {
    window.location.href = "/investment.html";
  };

  return (
    <div onClick={handleCardClick} className="cursor-pointer w-fit">
      <Card
        isBlurred
        className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-700 dark:to-green-500 max-w-[400px] min-h-[329px] max-h-[329px] p-6 shadow-lg transition-transform transform hover:scale-105"
      >
        <CardBody>
          <div className="flex flex-col items-start">
            <h2 style={{ fontSize: "30px", fontWeight: "bold" }}>Your Investments</h2>
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
          <div className="mt-6">
            {/* Downsample the data by taking every 4th row */}
            <StockGraph height="h-40" sampleInterval={4} />
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
