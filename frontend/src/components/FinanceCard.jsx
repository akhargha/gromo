import React from "react";
import { Card, CardBody, Button } from "@heroui/react";

export default function FinanceCard() {
  return (
    <Card
      isBlurred
      className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-800 dark:to-green-600 max-w-[800px] min-h-[329px] max-h-[329px] p-6 shadow-lg"
    >
      <CardBody>
        {/* Main Title with Black Border Outline */}
        <div className="flex flex-col items-start">
        <h2
            style={{
              fontSize: "30px",
              fontWeight: "bold"
            }}
          >
            Account Overview
          </h2>
          <p className="text-lg text-white/80">Your financial summary</p>
        </div>

        {/* Financial Details */}
        <div className="grid grid-cols-3 gap-6 mt-6">
          {/* Current Balance */}
          <Card className="p-4 bg-green-300 border border-black shadow-sm">
            <CardBody className="text-center">
              <h3 className="text-sm text-black font-semibold">Current Balance</h3>
              <p className="text-xl font-bold text-black">$12,450.00</p>
            </CardBody>
          </Card>

          {/* Available Credit */}
          <Card className="p-4 bg-green-300 border border-black shadow-sm">
            <CardBody className="text-center">
              <h3 className="text-sm text-black font-semibold">Available Credit</h3>
              <p className="text-xl font-bold text-black">$5,300.00</p>
            </CardBody>
          </Card>

          {/* Rewards Cash */}
          <Card className="p-4 bg-green-300 border border-black shadow-sm">
            <CardBody className="text-center">
              <h3 className="text-sm text-black font-semibold">Rewards Cash</h3>
              <p className="text-xl font-bold text-black">$220.50</p>
            </CardBody>
          </Card>
        </div>

        {/* Actions (Button Moved to Left) */}
        <div className="flex justify-start mt-6">
          <Button color="success" variant="ghost">
            Make Payment
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
