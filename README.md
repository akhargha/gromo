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
- GET /portfolios
Returns available investment portfolios with metadata and stock allocations.
- POST /invest
Processes manual investment requests.
jsonCopy{
  "amount": "50.00",
  "portfolio": "S&P 500"
}
- POST /auto_invest
Triggers automatic investment of accumulated cashback.
- GET /investment_summary
Returns comprehensive investment details and allocations.
- GET /investment_performance
Provides real-time performance metrics for investments.


### Update .env with your database credentials and API keys


## Future Enhancements

- Integration with public stock market APIs
- Multi-user support with authentication
- Advanced scheduling for automated investments
- Enhanced reporting and analytics
- Mobile application support
- Real-time transaction notifications
- Advanced portfolio rebalancing features
