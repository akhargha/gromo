import React, { useEffect, useState } from "react";
import { Card, CardBody, Button } from "@heroui/react";

const CARD_URL = "http://localhost:5001/credit_card"; // Backend API URL

export default function RewardCard() {
  const [rewardAmount, setRewardAmount] = useState("Loading...");
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

        const creditCard = data[0]; // Extract first row
        setRewardAmount(`$${(creditCard.rewards_cash || 0).toFixed(2)}`);
      })
      .catch((error) => {
        console.error("Error fetching reward amount:", error);
        setError("Failed to load rewards cash. Please try again later.");
      });
  }, []);

  return (
    <Card className="p-4 bg-green-300 border border-black shadow-sm max-w-[300px]">
      <CardBody className="flex flex-col items-center">
        {/* Reward Title */}
        <h2 className="text-lg text-black font-semibold">Reward Cash</h2>

        {/* Reward Amount */}
        {error ? (
          <p className="text-red-500 mt-2">{error}</p>
        ) : (
          <p className="text-2xl font-bold text-black mt-2" style={{ paddingBottom: "40px" }}>
            {rewardAmount}
          </p>
        )}

        {/* Action Buttons with Increased Spacing */}
        <div className="flex flex-col gap-6 mt-6">
          <Button color="success" size="lg" variant="solid" className="min-w-[150px] max-w-[150px]">
            Invest Now
          </Button>
          <Button color="success" size="lg" variant="solid" className="min-w-[150px] max-w-[150px]">
            Redeem for Cash
          </Button>
          <Button color="success" size="lg" variant="solid" className="min-w-[150px] max-w-[150px]">
            Claim Earnings
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
