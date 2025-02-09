import NavbarTop from "./components/NavbarTop";
import FinanceCard from "./components/FinanceCard.jsx";
import InvestmentCard from "./components/InvestmentCard.jsx";

export default function App() {
  return (
    <div className="relative min-h-screen">
      {/* Background Gradient for the Whole Page */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-400 via-green-500 to-green-600 dark:from-green-900 dark:via-green-900 dark:to-green-400"></div>
      
      {/* Navbar (Overlayed) */}
      <div className="relative z-10">
        <NavbarTop />
      </div>

      {/* Content Positioned Below the Navbar */}
      <div className="relative z-10 flex flex-row justify-center items-start mt-10 gap-10">
        <FinanceCard />
        <InvestmentCard investmentAmount="592" changePercentage="-10"/>
      </div>
    </div>
  );
}
