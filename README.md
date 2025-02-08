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
CREATE TABLE credit_cards (
    id SERIAL PRIMARY KEY,
    cc_number VARCHAR(20) NOT NULL,
    credit_line NUMERIC(10,2) NOT NULL,
    available_credit NUMERIC(10,2) NOT NULL DEFAULT 0,
    current_balance NUMERIC(10,2) NOT NULL DEFAULT 0,
    rewards_cash NUMERIC(10,2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


- transactions
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    credit_card_id INTEGER NOT NULL,
    cc_number VARCHAR(20) NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_amount NUMERIC(10,2) NOT NULL,
    description TEXT,
    FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id)
);

- investments
CREATE TABLE investments (
    id SERIAL PRIMARY KEY,
    credit_card_id INTEGER NOT NULL,
    investment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    investment_amount NUMERIC(10,2) NOT NULL,
    portfolio VARCHAR(100) NOT NULL,
    FOREIGN KEY (credit_card_id) REFERENCES credit_cards(id)
);

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
