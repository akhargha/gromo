import React from "react";
import { Card, CardBody, Button } from "@heroui/react";

export default function RewardCard({ rewardAmount }) {
  return (
    <Card className="p-4 bg-green-300 border border-black shadow-sm max-w-[300px]">
      <CardBody className="flex flex-col items-center">
        {/* Reward Title */}
        <h2 className="text-lg text-black font-semibold">Reward Cash</h2>

        {/* Reward Amount */}
        <p className="text-2xl font-bold text-black mt-2" style={{ paddingBottom: "40px"}}>${rewardAmount}</p>

        {/* Action Buttons with Increased Spacing */}
        <div className="flex flex-col gap-6 mt-6">
          <Button color="success" size="lg" variant="solid" className="min-w-[150px] max-w-[150px]">
            Invest Now
          </Button>
          <Button color="success" size="lg" variant="solid" className="min-w-[150px] max-w-[150px]">
            Redeem for Cash
          </Button>
          <Button color="success" size="lg" variant="solid" className="min-w-[150px] max-w-[150px]">
            Claim earnings
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
