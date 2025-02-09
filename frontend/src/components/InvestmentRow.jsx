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

// Sample transaction data with added Index column
const transactions = [
  {
    key: "1",
    index: "Vanguard Mid-capex", // Added index column
    date: "2024-02-01",
    amount: "$150.75",
  },
  {
    key: "2",
    index: "Vanguard Mid-capex",
    date: "2024-02-02",
    amount: "$85.20",
  },
  {
    key: "3",
    index: "Vanguard Mid-capex",
    date: "2024-02-03",
    amount: "$220.00",
  },
  {
    key: "4",
    index: "Vanguard Mid-capex",
    date: "2024-02-04",
    amount: "$45.60",
  },
];

// Updated Table column structure (added Index column)
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
    key: "index",
    label: "INDEX",
  },
];

export default function InvestmentRow() {
  return (
    <Card
      isBlurred
      className="border-1 border-black bg-gradient-to-br from-green-600 via-green-700 to-green-800 dark:from-green-900 dark:via-green-600 dark:to-green-600 min-w-[700px] max-w-[700px] p-6 shadow-lg"
    >
      <CardBody>
        <div className="flex flex-col items-start">
          <h2
            style={{
              fontSize: "30px",
              fontWeight: "bold",
            }}
          >
            Investments
          </h2>
          <p className="text-lg text-white/80">Your investment history</p>
        </div>

        <Table aria-label="Investment History">
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
                {(columnKey) => <TableCell>{getKeyValue(item, columnKey)}</TableCell>}
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardBody>
    </Card>
  );
}
