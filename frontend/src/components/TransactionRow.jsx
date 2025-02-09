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

// Define correct backend URL
const TRANSACTIONS_URL = "http://127.0.0.1:5003/transactions";

export default function TransactionRow() {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    fetch(TRANSACTIONS_URL)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        if (!Array.isArray(data) || data.length === 0) {
          throw new Error("No transactions found");
        }

        const formattedTransactions = data.map((tx) => ({
          key: tx.id,
          date: new Date(tx.transaction_date).toLocaleDateString(),
          amount: `$${tx.amount.toFixed(2)}`,
          cashback: `$${tx.cashback.toFixed(2)}`,
          invested: tx.invested ? "Yes" : "No",
        }));

        setTransactions(formattedTransactions);
      })
      .catch((error) => console.error("Error fetching transactions:", error));
  }, []);

  // Table columns
  const columns = [
    { key: "date", label: "TRANSACTION DATE" },
    { key: "amount", label: "AMOUNT ($)" },
    { key: "cashback", label: "CASHBACK EARNED ($)" },
  ];

  return (
    <Card
      isBlurred
      className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-600 dark:to-green-600 min-w-[800px] max-w-[1000px] p-6 shadow-lg"
    >
      <CardBody>
        <div className="flex flex-col items-start">
          <h2 style={{ fontSize: "30px", fontWeight: "bold" }}>Transactions</h2>
          <p className="text-lg text-white/80">Your recent transactions</p>
        </div>

        <Table aria-label="Transaction History">
          <TableHeader columns={columns}>
            {(column) => (
              <TableColumn key={column.key} className="text-white text-sm">
                {column.label}
              </TableColumn>
            )}
          </TableHeader>

          <TableBody items={transactions}>
            {(item) => (
              <TableRow key={item.key}>
                {(columnKey) => (
                  <TableCell
                    className={
                      columnKey === "cashback" ? "text-green-500 font-semibold" : ""
                    }
                  >
                    {item[columnKey]}
                  </TableCell>
                )}
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardBody>
    </Card>
  );
}
