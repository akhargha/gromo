from flask import Flask, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from supabase import create_client, Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# -------------------------------
# Supabase Setup
# -------------------------------
# Replace these with your actual Supabase credentials or set them as environment variables.
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dicdnvswymiaugijpjfa.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRpY2RudnN3eW1pYXVnaWpwamZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwMzYzNDAsImV4cCI6MjA1NDYxMjM0MH0.piFtbs8TCzvYAl-5htYNcl-fdAYkoqJEeIaUDz_iCI4")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------
# Yahoo Finance Data Fetching
# -------------------------------
def get_weekly_data(ticker, start_date, end_date):
    """
    Fetches weekly price data for a given ticker from Yahoo Finance between
    start_date and end_date.
    """
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
    params = {
        'period1': int(start_date.timestamp()),
        'period2': int(end_date.timestamp()),
        'interval': '1wk',
    }
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()['chart']['result'][0]

        timestamps = data['timestamp']
        closes = data['indicators']['quote'][0]['close']

        # Create a DataFrame of weekly dates and closing prices.
        df = pd.DataFrame({
            'Date': pd.to_datetime(timestamps, unit='s'),
            'Close': closes
        }).dropna().sort_values("Date").reset_index(drop=True)

        return df

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# -------------------------------
# Portfolio Endpoint
# -------------------------------
@app.route('/portfolio', methods=['GET'])
def portfolio():
    # -------------------------------
    # Fetch All Transactions for user_investment_id 4 from Supabase
    # -------------------------------
    tx_response = supabase.table("investment_transactions") \
                          .select("*") \
                          .eq("user_investment_id", 4) \
                          .execute()
    transactions_data = tx_response.data

    if not transactions_data:
        return jsonify({"error": "No transactions found"}), 404

    # -------------------------------
    # Process Transactions & Determine Portfolio Timeframe
    # -------------------------------
    # Mapping: user_investment_id 4 → ticker "VOO"
    ticker_mapping = {4: "VOO"}

    transactions = []
    for tx in transactions_data:
        try:
            tx_date = datetime.fromisoformat(tx["investment_date"])
        except Exception as e:
            print(f"Error parsing date for transaction id {tx.get('id')}: {e}")
            continue

        ticker = ticker_mapping.get(tx["user_investment_id"])
        if not ticker:
            continue  # Skip transactions with no ticker mapping.

        transactions.append({
            "date": tx_date,
            "ticker": ticker,
            "shares": float(tx["units_purchased"])
        })

    # Ensure we have at least one transaction
    if not transactions:
        return jsonify({"error": "No valid transactions found"}), 404

    # Sort transactions by date (earliest first)
    transactions = sorted(transactions, key=lambda x: x["date"])

    # Define the portfolio period: start on the first investment date, lasting 52 weeks.
    portfolio_start_date = transactions[0]["date"]
    portfolio_end_date = portfolio_start_date + timedelta(weeks=52)

    # Filter transactions to only include those within the one-year window.
    transactions = [tx for tx in transactions if tx["date"] <= portfolio_end_date]

    # -------------------------------
    # Fetch Price Data for the Ticker(s)
    # -------------------------------
    tickers = list({tx["ticker"] for tx in transactions})
    ticker_data = {}
    for ticker in tickers:
        df = get_weekly_data(ticker, start_date=portfolio_start_date, end_date=portfolio_end_date)
        if df is None:
            return jsonify({"error": f"Failed to fetch data for ticker {ticker}"}), 500
        ticker_data[ticker] = df

    # -------------------------------
    # Generate a Weekly Portfolio Time Series
    # -------------------------------
    # Create a list of weekly dates for the one-year period.
    week_dates = pd.date_range(start=portfolio_start_date, end=portfolio_end_date, freq='W')
    result = []

    for week_date in week_dates:
        week_dt = week_date.to_pydatetime()
        # Compute cumulative holdings: add up units from transactions that occurred on or before this week.
        holdings = {}
        for tx in transactions:
            if tx["date"] <= week_dt:
                holdings[tx["ticker"]] = holdings.get(tx["ticker"], 0) + tx["shares"]

        # Compute portfolio value for this week.
        portfolio_value = 0.0
        for ticker, shares in holdings.items():
            df = ticker_data[ticker]
            # Retrieve the price at or immediately after the current week date.
            df_filtered = df[df["Date"] >= week_dt]
            if not df_filtered.empty:
                price = df_filtered.iloc[0]["Close"]
            else:
                price = df.iloc[-1]["Close"]
            portfolio_value += shares * price

        result.append({
            "x": week_dt.strftime("%Y-%m-%d"),
            "y": round(portfolio_value, 2),
            "holdings": {ticker: round(shares, 4) for ticker, shares in holdings.items()}
        })

    # Return the 52 weekly data points as JSON.
    return jsonify(result)

if __name__ == '__main__':
    # For development purposes. In production, use a proper WSGI server.
    app.run(debug=True)
