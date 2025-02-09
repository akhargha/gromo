import React, { useEffect, useState } from "react";
import { Card, CardBody, Button } from "@heroui/react";

const CARD_URL = "http://localhost:5001/credit_card"; // Backend API URL

export default function FinanceCard() {
  const [creditData, setCreditData] = useState({
    current_balance: "Loading...",
    available_credit: "Loading...",
    rewards_cash: "Loading...",
  });

  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(CARD_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (!Array.isArray(data) || data.length === 0) {
          throw new Error("No credit card data found");
        }

        const creditCard = data[0]; // Extract the first row

        setCreditData({
          current_balance: `$${(creditCard.curr_balance || 0).toFixed(2)}`,
          available_credit: `$${(creditCard.available_credit || 0).toFixed(2)}`,
          rewards_cash: `$${(creditCard.rewards_cash || 0).toFixed(2)}`,
        });
      })
      .catch((error) => {
        console.error("Error fetching credit card data:", error);
        setError("Failed to load financial data. Please try again later.");
      });
  }, []);

  return (
    <Card
      isBlurred
      className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-800 dark:to-green-600 max-w-[800px] min-h-[329px] max-h-[329px] p-6 shadow-lg"
    >
      <CardBody>
        <div className="flex flex-col items-start">
          <h2 style={{ fontSize: "30px", fontWeight: "bold" }}>Account Overview</h2>
          <p className="text-lg text-white/80">Your financial summary</p>
        </div>

        {error ? (
          <div className="text-red-500 text-center mt-4">{error}</div>
        ) : (
          <div className="grid grid-cols-3 gap-6 mt-6">
            <Card className="p-4 bg-green-300 border border-black shadow-sm">
              <CardBody className="text-center">
                <h3 className="text-sm text-black font-semibold">Current Balance</h3>
                <p className="text-xl font-bold text-black">{creditData.current_balance}</p>
              </CardBody>
            </Card>

            <Card className="p-4 bg-green-300 border border-black shadow-sm">
              <CardBody className="text-center">
                <h3 className="text-sm text-black font-semibold">Available Credit</h3>
                <p className="text-xl font-bold text-black">{creditData.available_credit}</p>
              </CardBody>
            </Card>

            <Card className="p-4 bg-green-300 border border-black shadow-sm">
              <CardBody className="text-center">
                <h3 className="text-sm text-black font-semibold">Rewards Cash</h3>
                <p className="text-xl font-bold text-black">{creditData.rewards_cash}</p>
              </CardBody>
            </Card>
          </div>
        )}

        <div className="flex justify-start mt-6">
          <Button color="success" variant="ghost">
            Make Payment
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
