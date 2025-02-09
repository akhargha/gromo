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

// Define backend URL as a variable
const TRANSACTIONS_URL = "http://127.0.0.1:5006"; // You can change this easily if needed

export default function TransactionRow() {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    // Fetch transactions from backend
    fetch(`${TRANSACTIONS_URL}/transactions`)
      .then((response) => response.json())
      .then((data) => {
        // Map the received transactions to the required format
        const formattedTransactions = data.map((tx, index) => ({
          key: tx.id.toString(),
          date: new Date(tx.transaction_date).toLocaleDateString(),
          amount: `$${tx.transaction_amount.toFixed(2)}`,
          type: tx.description, // Use description for transaction type
          cashback: `$${(tx.transaction_amount * 0.03).toFixed(2)}`, // 3% cashback
        }));

        setTransactions(formattedTransactions);
      })
      .catch((error) => console.error("Error fetching transactions:", error));
  }, []);

  // Table column structure
  const columns = [
    {
      key: "date",
      label: "TRANSACTION DATE",
    },
    {
      key: "amount",
      label: "AMOUNT ($)",
    },
    {
      key: "type",
      label: "TRANSACTION TYPE",
    },
    {
      key: "cashback",
      label: "CASHBACK EARNED ($)",
    },
  ];

  return (
    <Card
      isBlurred
      className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-600 dark:to-green-600 min-w-[1000px] max-w-[1000px] p-6 shadow-lg"
    >
      <CardBody>
        <div className="flex flex-col items-start">
          <h2 style={{ fontSize: "30px", fontWeight: "bold" }}>Transactions</h2>
          <p className="text-lg text-white/80">Your recent transactions</p>
        </div>

        <Table aria-label="Transaction History">
          {/* Table Header */}
          <TableHeader columns={columns}>
            {(column) => (
              <TableColumn key={column.key} className="text-white text-sm">
                {column.label}
              </TableColumn>
            )}
          </TableHeader>

          {/* Table Body */}
          <TableBody items={transactions}>
            {(item) => (
              <TableRow key={item.key}>
                {(columnKey) => (
                  <TableCell className={columnKey === "cashback" ? "text-green-500 font-semibold" : ""}>
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
