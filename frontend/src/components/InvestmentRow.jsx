import React, { useEffect, useState } from "react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Card,
  CardBody,
} from "@heroui/react";

// Define backend API URL
const INVESTMENTS_URL = "http://127.0.0.1:5002/investments";

export default function InvestmentRow() {
  const [investments, setInvestments] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(INVESTMENTS_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (!Array.isArray(data) || data.length === 0) {
          throw new Error("No investments found");
        }

        const formattedInvestments = data.map((investment) => ({
          key: investment.id,
          date: new Date(investment.date).toLocaleDateString(),
          index: investment.index_purchased || "Unknown",
          units: investment.units_purchased.toFixed(4),
          pricePerUnit: `$${investment.price_per_unit.toFixed(2)}`,
          amount: `$${investment.amount_invested.toFixed(2)}`,
        }));

        setInvestments(formattedInvestments);
      })
      .catch((error) => {
        console.error("Error fetching investments:", error);
        setError("Failed to load investment data. Please try again later.");
      })
      .finally(() => setLoading(false));
  }, []);

  const columns = [
    { key: "date", label: "TRANSACTION DATE" },
    { key: "index", label: "INDEX" },
    { key: "units", label: "UNITS PURCHASED" },
    { key: "pricePerUnit", label: "PRICE PER UNIT ($)" },
    { key: "amount", label: "AMOUNT INVESTED ($)" },
  ];

  return (
    <Card
      isBlurred
      className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-600 dark:to-green-600 min-w-[1020px] max-w-[1020px] p-6 shadow-lg"
    >
      <CardBody>
        <div className="flex flex-col items-start">
          <h2 style={{ fontSize: "30px", fontWeight: "bold" }}>Investments</h2>
          <p className="text-lg text-white/80">Your investment history</p>
        </div>

        {loading ? (
          <p className="text-white mt-4">Loading investments...</p>
        ) : error ? (
          <div className="text-red-500 text-center mt-4">{error}</div>
        ) : investments.length === 0 ? (
          <p className="text-white mt-4">No investments found.</p>
        ) : (
          <Table aria-label="Investment History">
            <TableHeader columns={columns}>
              {(column) => (
                <TableColumn key={column.key} className="text-white text-sm">
                  {column.label}
                </TableColumn>
              )}
            </TableHeader>

            <TableBody items={investments}>
              {(item) => (
                <TableRow key={item.key}>
                  {(columnKey) => <TableCell>{item[columnKey]}</TableCell>}
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </CardBody>
    </Card>
  );
}
