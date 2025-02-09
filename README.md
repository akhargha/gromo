# 💸 Gromo: Put Your Lazy Money to Work

## Turn your credit card cashback into smart investments

<div align="center">
  <img src="logo_name.png" alt="Gromo Logo" width="1000" style="border-radius: 30px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
</div>

> Gromo revolutionizes the way you handle credit card cashback. Don't let your rewards sit idle – invest them for long-term growth!

<div align="center">

[Overview](#-overview) •
[Features](#-key-features) •
[How It Works](#-how-it-works) •
[Tech Stack](#-tech-stack) •
[Getting Started](#-getting-started)

</div>

## 🚀 Overview

Gromo is a proof-of-concept cashback investment platform that automates the process of investing your credit card rewards. By putting your "lazy money" to work, Gromo helps you maximize the potential of your cashback through smart, diversified investments in ETFs and other long-term options.

### The Problem
- Unused or underutilized credit card cashback rewards
- Lack of easy options to invest small, regular cashback amounts
- Missed opportunities for long-term growth of reward money

### Our Solution
- Automated cashback tracking and investment
- Diversified investment options based on risk preference
- Real-time performance tracking and portfolio management

## 🌟 Key Features

### 1. Smart Transaction Logging
- Automatic purchase logging from partner websites
- Dynamic cashback calculation for each transaction

### 2. Flexible Investment Options
- Manual investment of cashback rewards
- Automated monthly investment based on portfolio performance
- Risk-based portfolio selection

### 3. Real-time Performance Tracking
- Monitor investment performance metrics
- View current stock value and number of shares
- Track today's return and total return

### 4. Credit Card Management
- Track balances and available credit
- Monitor cashback rewards accumulation

<div className="flex flex-col items-center gap-5 my-5">
      <img
        src="https://github.com/user-attachments/assets/2c1389e9-2545-4fd6-bf52-75e9abf629f7"
        alt="ss1"
        className="w-[800px] rounded-[30px] shadow-lg"
      />
      <img
        src="https://github.com/user-attachments/assets/08958e66-8e48-45d3-9433-a8c486580efc"
        alt="ss2"
        className="w-[800px] rounded-[30px] shadow-lg"
      />
    </div>

## 🔄 How It Works

1. **Connect Your Card**: Link your credit card to start tracking cashback.
2. **Earn Cashback**: Make purchases and accumulate rewards.
3. **Choose Your Strategy**: Opt for manual or automated investments.
4. **Invest & Grow**: Watch your cashback turn into long-term investments.
5. **Track Performance**: Monitor your portfolio's growth in real-time.

<div className="flex justify-center my-5">
      <img
        src="https://github.com/user-attachments/assets/c953a79f-5e56-419a-8d38-0961a0081359"
        alt="Gromo Process"
        className="w-[800px] rounded-[30px] shadow-lg"
      />
</div>


## 💻 Tech Stack

<div align="center">

### Frontend
![React](https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react)
![Vite](https://img.shields.io/badge/Vite-5.x-646CFF?style=for-the-badge&logo=vite)

### Backend
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-Latest-red?style=for-the-badge)

### Database
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-336791?style=for-the-badge&logo=postgresql)
![Supabase](https://img.shields.io/badge/Supabase-Hosting-3ECF8E?style=for-the-badge&logo=supabase)

</div>



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

### creditCard

#### Fields
- id
- credit_line
- available_credit
-rewards_cash

### transactions

#### Fields
- id
- transaction_date DEFAULT Now()
- amount
- cashback
- invested

### investments

#### Fields
- id
- date
- amount_invested
- index
- units_purchased
- price_per_unit

### portfolio

#### Fields
- id
- date
- price_per_unit
- no_of_units

## API Endpoints

### Credit Card Management
- GET /credit_card 
- PUT /credit_card

### Investment Section

- GET /investments
- GET /investments/total
- GET /investments/invest-reward
- GET /investment_chart

### Transaction Management

- POST /transactions
- GET /transactions
- POST /transactions/invest/<transaction_id>



## Future Enhancements

- Integration with public stock market APIs
- Multi-user support with authentication
- Advanced scheduling for automated investments
- Enhanced reporting and analytics
- Mobile application support
- Real-time transaction notifications
- Advanced portfolio rebalancing features
