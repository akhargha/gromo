import React, { useEffect } from "react";
import NavbarTop from "./components/NavbarTop";
import FinanceCard from "./components/FinanceCard.jsx";
import InvestmentCard from "./components/InvestmentCard.jsx";
import TransactionRow from "./components/TransactionRow.jsx";

const CARD_BASE_URL = "http://localhost:5005"; // Store the backend API base URL

export default function App() {
  useEffect(() => {
    fetch(`${CARD_BASE_URL}/update_credit_cards`)
      .then((response) => response.json())
      .then((data) => console.log("Credit Cards Updated:", data))
      .catch((error) => console.error("Error updating credit cards:", error));
  }, []);

  return (
    <div className="relative min-h-screen">
      {/* Background Gradient for the Whole Page */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-400 via-green-500 to-green-600 dark:from-green-900 dark:via-green-900 dark:to-green-400"></div>
      
      {/* Navbar (Overlayed) */}
      <div className="relative z-10">
        <NavbarTop />
      </div>

      {/* Cards Section (Finance & Investment Side by Side) */}
      <div className="relative z-10 flex flex-row justify-center items-start mt-10 gap-10">
        <FinanceCard />
        <InvestmentCard investmentAmount="592" changePercentage="-11"/>
      </div>

      {/* Transaction Table - Centered with Gap */}
      <div className="relative z-10 flex justify-center mt-10" style={{ paddingBottom: "80px"}}>
        <div className="w-full max-w-4xl flex justify-center"> {/* Centered & Limited Width */}
          <TransactionRow />
        </div>
      </div>
    </div>
  );
}
