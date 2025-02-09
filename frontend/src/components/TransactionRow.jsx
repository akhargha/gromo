import React from "react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  getKeyValue,
  Card,
  CardBody,
} from "@heroui/react";

// Sample transaction data
const transactions = [
  {
    key: "1",
    date: "2024-02-01",
    amount: "$150.75",
    type: "Groceries",
  },
  {
    key: "2",
    date: "2024-02-02",
    amount: "$85.20",
    type: "Fashion",
  },
  {
    key: "3",
    date: "2024-02-03",
    amount: "$220.00",
    type: "Electronics",
  },
  {
    key: "4",
    date: "2024-02-04",
    amount: "$45.60",
    type: "Dining",
  },
];

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
];

export default function TransactionRow() {
  return (
    <Card
      isBlurred
      className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-800 dark:to-green-600 min-w-[1000px] max-w-[1000px] p-6 shadow-lg"
    >
      <CardBody>
        <div className="flex flex-col items-start">
          <h2
            style={{
              fontFamily: "sans-serif",
              color: "white",
              textShadow:
                "1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000",
              fontSize: "30px",
            }}
          >
            Transactions
          </h2>
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
                  <TableCell>{getKeyValue(item, columnKey)}</TableCell>
                )}
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardBody>
    </Card>
  );
}
