# gromo
A hackathon project demonstrating automatic investment of credit card cashback rewards.


# Overview
The Cashback Investment Platform is a proof-of-concept application that automates the investment of credit card cashback rewards. The platform handles transaction logging, cashback calculations, and investment management through both manual and automated processes.

## Features

- Transaction Logging: Automatically logs purchases from partner websites
Dynamic Cashback Calculation: Computes cashback rewards for each transaction
- Credit Card Management: Tracks balances, available credit, and rewards
Investment Options:

- Manual investment of cashback rewards
- Automated monthly investment based on portfolio performance
- Performance Tracking: Real-time monitoring of investment performance metrics
- Today's return
- Total return
- Current stock value
- Number of shares held

- Manual Investment

Allows users to invest specific amounts from their available cashback rewards
Supports portfolio selection based on risk preference
Automatically allocates investments across stocks based on portfolio weights
Provides immediate confirmation with detailed allocation information

- Auto-Investment

Automatically invests all available cashback into the best-performing portfolio
Uses historical return data to select optimal portfolio
Handles complete allocation across portfolio stocks
Provides detailed investment confirmation

- Investment Tracking

Real-time monitoring of investment performance
Detailed view of stock allocations
Current value calculations
Performance metrics including returns



## Tech Stack

Frontend: React with Vite
Backend: Flask (Python) with SQLAlchemy ORM
Database: PostgreSQL (hosted on Supabase)
Optional: External APIs for stock price updates (Yahoo Finance, IEX Cloud)

## System Architecture
Application Layers
Frontend (React + Vite)

## User interface providing:

- Credit card and transaction summaries
- Manual investment controls
- Investment performance dashboards

### Backend (Flask)

RESTful API endpoints for:

- Transaction and cashback processing
- Credit card data management
- Investment processing (manual and automatic)
- Performance metric calculations

### Database (PostgreSQL/Supabase)
- Stores all application data including:

- Credit card information
- Transactions and cashback
- Investment records
- Portfolio configurations
- Stock data

## Data Flow

- Transaction Processing

- Records new purchases
- Calculates and stores cashback
- Updates credit card balances


## Investment Processing

- Manual: User-initiated investment into selected portfolio
- Automatic: Monthly investment based on portfolio performance
Stock allocation based on portfolio weights


## Performance Tracking

- Real-time stock price updates
- Return calculations
- Portfolio valuation



## Database Schema

- credit_cards
Stores credit card summary data.

CREATE TABLE credit_cards (
    id SERIAL PRIMARY KEY,
    cc_number VARCHAR(20) NOT NULL,
    credit_line NUMERIC(10,2) NOT NULL,
    available_credit NUMERIC(10,2) NOT NULL DEFAULT 0,
    current_balance NUMERIC(10,2) NOT NULL DEFAULT 0,
    rewards_cash NUMERIC(10,2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Purpose: Holds the current status of the credit card. All transactions and investments are associated with this single record.

- transactions
Logs every checkout transaction.
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    credit_card_id INTEGER NOT NULL,  -- Foreign key to credit_cards
    cc_number VARCHAR(20) NOT NULL,     -- Redundant copy for convenience
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_amount NUMERIC(10,2) NOT NULL,
    description TEXT,
    FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id)
);

Purpose: Records purchase transactions for later processing.

- cashback_transactions
Stores the cashback amount computed for each transaction.
CREATE TABLE cashback_transactions (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER NOT NULL,  -- Foreign key to transactions
    cashback_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    transaction_amount NUMERIC(10,2) NOT NULL,  -- Mirrors transaction amount
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

Purpose: Separates the cashback logic from the transaction record to allow dynamic changes in cashback rules.

- investments
Records each investment event.
CREATE TABLE investments (
    id SERIAL PRIMARY KEY,
    credit_card_id INTEGER NOT NULL,  -- Foreign key to credit_cards
    investment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    investment_amount NUMERIC(10,2) NOT NULL,
    portfolio VARCHAR(100) NOT NULL,  -- Name of the chosen portfolio
    FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id)
);
Purpose: Logs the total amount invested in a given action along with the portfolio selected.
Investment Management Tables

- portfolios
Stores metadata about available portfolios.

CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    historical_return NUMERIC(5,2),  -- Average historical return (percentage)
    risk_level VARCHAR(50),          -- e.g., 'Low', 'Medium', 'High'
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Purpose: Defines investment options and tracks their historical performance.

- stocks
Stores details for individual stocks.

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100),
    current_price NUMERIC(10,2) NOT NULL DEFAULT 0,
    previous_close NUMERIC(10,2) NOT NULL DEFAULT 0,  -- Used for calculating today's return
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Purpose: Contains stock pricing data, updated periodically via external APIs.

- portfolio_stocks
Maps stocks to portfolios with defined allocation weights.

CREATE TABLE portfolio_stocks (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL,  -- Foreign key to portfolios
    stock_id INTEGER NOT NULL,      -- Foreign key to stocks
    weight NUMERIC(5,2) NOT NULL,     -- Percentage weight (e.g., 20.00 means 20%)
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

Purpose: Specifies how much of an investment should be allocated to each stock within a portfolio.

- investment_details
Breaks down each investment into individual stock positions.

CREATE TABLE investment_details (
    id SERIAL PRIMARY KEY,
    investment_id INTEGER NOT NULL,  -- Foreign key to investments
    stock_id INTEGER NOT NULL,       -- Foreign key to stocks
    units NUMERIC(10,4) NOT NULL,      -- Number of shares purchased
    purchase_price NUMERIC(10,2) NOT NULL,  -- Stock price at purchase
    FOREIGN KEY (investment_id) REFERENCES investments(id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
);

Purpose: Records the detailed allocation of an investment across various stocks.


## API Endpoints


### Investment Section
Investment Endpoints
1. Manual Investment
Create a new investment using available cashback rewards.
POST /api/invest
Request Body:
jsonCopy{
    "amount": "50.00",
    "portfolio": "Tech Growth"
}
Success Response (200 OK):
jsonCopy{
    "message": "Investment completed",
    "portfolio": "Tech Growth",
    "amount_invested": "50.00",
    "allocations": [
        {
            "stock_symbol": "AAPL",
            "units": "0.2500",
            "amount_allocated": "25.00"
        },
        {
            "stock_symbol": "GOOGL",
            "units": "0.1500",
            "amount_allocated": "15.00"
        }
    ]
}
Error Responses:

400 Bad Request: Invalid input data
404 Not Found: Portfolio not found
500 Internal Server Error: Processing failed

2. Automatic Investment
Automatically invest all available cashback into the best-performing portfolio.
CopyPOST /api/auto_invest
Success Response (200 OK):
jsonCopy{
    "message": "Auto-investment completed",
    "portfolio": "Tech Growth",
    "amount_invested": "150.00",
    "allocations": [
        {
            "stock_symbol": "AAPL",
            "units": "0.7500",
            "amount_allocated": "75.00"
        },
        {
            "stock_symbol": "GOOGL",
            "units": "0.4500",
            "amount_allocated": "45.00"
        }
    ]
}
Error Responses:

400 Bad Request: No cashback available
404 Not Found: No portfolio or credit card found
500 Internal Server Error: Processing failed

3. Investment Summary
Get a summary of all investments and their current values.
GET /api/investment_summary
Success Response (200 OK):
jsonCopy[
    {
        "investment_id": 1,
        "investment_date": "2025-02-08T18:16:01Z",
        "portfolio": "Tech Growth",
        "investment_amount": "50.00",
        "current_value": "52.50",
        "allocations": [
            {
                "stock_symbol": "AAPL",
                "units": "0.2500",
                "purchase_price": "100.00",
                "current_price": "105.00",
                "current_value": "26.25"
            },
            {
                "stock_symbol": "GOOGL",
                "units": "0.1500",
                "purchase_price": "150.00",
                "current_price": "155.00",
                "current_value": "23.25"
            }
        ]
    }
]
Error Response:

500 Internal Server Error: Failed to fetch data

4. Available Portfolios
Get list of available investment portfolios.
CopyGET /api/portfolios
Success Response (200 OK):
jsonCopy[
    {
        "id": 4,
        "name": "Tech Growth",
        "description": "High-growth technology stocks",
        "historical_return": "15.50",
        "risk_level": "High",
        "stocks": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "weight": "40.00"
            },
            {
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "weight": "35.00"
            }
        ]
    }
]
Error Response:

500 Internal Server Error: Failed to fetch portfolios

5. Performance Metrics
Get real-time performance metrics for investments.
GET /api/investment_performance
Success Response (200 OK):
jsonCopy[
    {
        "investment_detail_id": 1,
        "stock_symbol": "AAPL",
        "units": "0.2500",
        "purchase_price": "100.00",
        "current_price": "105.00",
        "current_value": "26.25",
        "total_return": "1.25",
        "todays_return": "0.50"
    }
]
Error Response:

500 Internal Server Error: Failed to fetch performance data

Example cURL Commands
Manual Investment:
bashCopycurl -X POST http://localhost:5000/api/invest \
  -H "Content-Type: application/json" \
  -H "apikey: your-supabase-key" \
  -d '{
    "amount": "50.00",
    "portfolio": "Tech Growth"
  }'
Auto-Investment:
bashCopycurl -X POST http://localhost:5000/api/auto_invest \
  -H "apikey: your-supabase-key"
Get Investment Summary:
bashCopycurl http://localhost:5000/api/investment_summary \
  -H "apikey: your-supabase-key"
Get Available Portfolios:
bashCopycurl http://localhost:5000/api/portfolios \
  -H "apikey: your-supabase-key"
Get Performance Metrics:
bashCopycurl http://localhost:5000/api/investment_performance \
  -H "apikey: your-supabase-key"




## Future Enhancements

- Integration with public stock market APIs
- Multi-user support with authentication
- Advanced scheduling for automated investments
- Enhanced reporting and analytics
- Mobile application support
- Real-time transaction notifications
- Advanced portfolio rebalancing features
