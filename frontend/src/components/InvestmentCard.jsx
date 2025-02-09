import React, { useState, useEffect } from "react";
import { Card, CardBody } from "@heroui/react";
import StockGraph from "./StockGraph";
import UpArrow from "../assets/up-arrow.svg";
import DownArrow from "../assets/arrow-down.svg";

const PORTFOLIO_URL = "http://localhost:8001/investment_chart";
const INVESTMENTS_URL = "http://localhost:5002/investments";

export default function InvestmentCard() {
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
        console.log("a" + lastPortfolioValue);
        console.log("b" + totalInvested);
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
            <StockGraph height="h-40" sampleInterval={4} />
          </div>
        </CardBody>
      </Card>
    </div>
  );
}