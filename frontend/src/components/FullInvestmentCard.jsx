import React, { useEffect, useState } from "react";
import { Card, CardBody } from "@heroui/react";
import StockGraph from "./StockGraph"; // Import the Chart.js graph
import UpArrow from "../assets/up-arrow.svg"; // Import Up Arrow
import DownArrow from "../assets/arrow-down.svg"; // Import Down Arrow

const PORTFOLIO_URL = "http://localhost:8001/investment_chart";
const INVESTMENTS_URL = "http://localhost:5002/investments";

export default function FullInvestmentCard() {
  const [investmentAmount, setInvestmentAmount] = useState(null);
  const [changePercentage, setChangePercentage] = useState(null);

  useEffect(() => {
    const fetchInvestmentData = async () => {
      try {
        const portfolioResponse = await fetch(PORTFOLIO_URL);
        const portfolioData = await portfolioResponse.json();
        const lastPortfolioValue = portfolioData[portfolioData.length - 1]?.portfolio_value;

        const investmentsResponse = await fetch(INVESTMENTS_URL);
        const investmentsData = await investmentsResponse.json();
        const totalInvested = investmentsData.reduce((sum, inv) => sum + inv.amount_invested, 0);

        setInvestmentAmount(lastPortfolioValue.toFixed(2));
        const change = ((lastPortfolioValue - totalInvested) / totalInvested) * 100;
        setChangePercentage(change.toFixed(2));
      } catch (error) {
        console.error("Error fetching investment data:", error);
      }
    };
    
    fetchInvestmentData();
  }, []);

  const isPositive = Number(changePercentage) >= 0;
  const textColor = isPositive ? "text-green-500" : "text-red-700";
  const arrowIcon = isPositive ? UpArrow : DownArrow;

  return (
    <div className="w-fit">
      <Card
        isBlurred
        className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-700 dark:to-green-500 max-w-[800px] min-w-[800px] min-h-[400px] max-h-[400px] p-6 shadow-lg transition-transform transform"
      >
        <CardBody>
          <div className="flex flex-col items-start">
            <h2 style={{ fontSize: "30px", fontWeight: "bold" }}>
              Your Portfolio
            </h2>
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
            <StockGraph height="h-56" />
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
