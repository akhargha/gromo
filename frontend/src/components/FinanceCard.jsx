import React from "react";
import { Card, CardBody, Button } from "@heroui/react";

export default function FinanceCard() {
  return (
    <Card
      isBlurred
      className="border-none bg-background/60 dark:bg-default-100/50 max-w-[800px] p-6 shadow-lg"
    >
      <CardBody>
        {/* Main Title */}
        <div className="flex flex-col items-start">
          <h2 className="text-2xl font-bold text-white">
            Account Overview
          </h2>
          <p className="text-lg text-white/80">Your financial summary</p>
        </div>

        {/* Financial Details */}
        <div className="grid grid-cols-3 gap-6 mt-6">
          {/* Current Balance */}
          <Card className="p-4 bg-green-100 border border-black shadow-sm">
            <CardBody className="text-center">
              <h3 className="text-sm text-black font-semibold">Current Balance</h3>
              <p className="text-xl font-bold text-black">$12,450.00</p>
            </CardBody>
          </Card>

          {/* Available Credit */}
          <Card className="p-4 bg-green-100 border border-black shadow-sm">
            <CardBody className="text-center">
              <h3 className="text-sm text-black font-semibold">Available Credit</h3>
              <p className="text-xl font-bold text-black">$5,300.00</p>
            </CardBody>
          </Card>

          {/* Rewards Cash */}
          <Card className="p-4 bg-green-100 border border-black shadow-sm">
            <CardBody className="text-center">
              <h3 className="text-sm text-black font-semibold">Rewards Cash</h3>
              <p className="text-xl font-bold text-black">$220.50</p>
            </CardBody>
          </Card>
        </div>

        {/* Actions */}
        <div className="flex justify-center mt-6">
          <Button color="success" variant="flat">
            View Details
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
