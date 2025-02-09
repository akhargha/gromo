import React, { useEffect, useState } from "react";
import { Card, CardBody, Button } from "@heroui/react";

// Define backend URL as a variable
const CARD_URL = "http://127.0.0.1:5005"; // Change this if needed

export default function RewardCard() {
  const [rewardAmount, setRewardAmount] = useState("0.00");

  useEffect(() => {
    // Fetch credit card details
    fetch(`${CARD_URL}/get_credit_cards`)
      .then((response) => response.json())
      .then((data) => {
        if (data.credit_cards && data.credit_cards.length > 0) {
          setRewardAmount(data.credit_cards[0].rewards_cash.toFixed(2)); // Get rewards cash
        }
      })
      .catch((error) => console.error("Error fetching reward amount:", error));
  }, []);

  return (
    <Card className="p-4 bg-green-300 border border-black shadow-sm max-w-[300px]">
      <CardBody className="flex flex-col items-center">
        {/* Reward Title */}
        <h2 className="text-lg text-black font-semibold">Reward Cash</h2>

        {/* Reward Amount */}
        <p className="text-2xl font-bold text-black mt-2" style={{ paddingBottom: "40px" }}>
          ${rewardAmount}
        </p>

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
