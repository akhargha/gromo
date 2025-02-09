from flask import Flask, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

def get_weekly_data(ticker, start_date, end_date):
    """
    Fetch one year of weekly data for the given ticker from Yahoo Finance,
    between start_date and end_date.
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
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(timestamps, unit='s'),
            'Close': closes
        }).dropna().sort_values("Date").reset_index(drop=True)
        
        return df
        
    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return None

@app.route('/portfolio', methods=['GET'])
def portfolio():
    # Define portfolio simulation period: the past 52 weeks.
    portfolio_end_date = datetime.now()
    portfolio_start_date = portfolio_end_date - timedelta(weeks=52)
    
    # -- MOCK TRANSACTION HISTORY --
    # For simplicity, we use transaction dates that align with our weekly data.
    # Each transaction is defined by the date, the ticker, and the dollar amount invested.
    # When a transaction occurs, we assume you buy shares at that week's closing price.
    transactions = [
        {"date": portfolio_start_date, "ticker": "VOO", "amount": 10},
        {"date": portfolio_start_date + timedelta(weeks=2), "ticker": "IVV", "amount": 20},
        {"date": portfolio_start_date + timedelta(weeks=4), "ticker": "SPY", "amount": 15},
        {"date": portfolio_start_date + timedelta(weeks=20), "ticker": "VOO", "amount": 25},
    ]
    
    # Get the unique tickers from the transactions.
    tickers = list({tx["ticker"] for tx in transactions})
    
    # -- FETCH WEEKLY PRICE DATA --
    # For each ticker, fetch one year of weekly data between portfolio_start_date and portfolio_end_date.
    ticker_data = {}
    for ticker in tickers:
        df = get_weekly_data(ticker, start_date=portfolio_start_date, end_date=portfolio_end_date)
        if df is None:
            return jsonify({"error": f"Failed to fetch data for {ticker}"}), 500
        ticker_data[ticker] = df

    # -- COMPUTE SHARES PURCHASED FOR EACH TRANSACTION --
    # For each transaction, find the first available weekly price on or after the transaction date
    # and compute the number of shares purchased.
    transaction_shares = []
    for tx in transactions:
        ticker = tx["ticker"]
        tx_date = tx["date"]
        df = ticker_data[ticker]
        # Find the first row where Date >= transaction date.
        df_filtered = df[df["Date"] >= tx_date]
        if not df_filtered.empty:
            tx_price = df_filtered.iloc[0]["Close"]
            shares = tx["amount"] / tx_price
        else:
            shares = 0  # fallback in case no data is available after the transaction date.
        tx_entry = tx.copy()
        tx_entry["shares"] = shares
        transaction_shares.append(tx_entry)
    
    # -- GENERATE A TIME SERIES (52 WEEKLY POINTS) FOR THE PORTFOLIO --
    # We create a series of weekly dates between portfolio_start_date and portfolio_end_date.
    week_dates = pd.date_range(start=portfolio_start_date, end=portfolio_end_date, freq='W')
    
    result = []
    for week_date in week_dates:
        week_date = week_date.to_pydatetime()  # convert pandas Timestamp to datetime
        # Determine the cumulative holdings as of this week.
        holdings = {}
        for tx in transaction_shares:
            if tx["date"] <= week_date:
                holdings[tx["ticker"]] = holdings.get(tx["ticker"], 0) + tx["shares"]
        
        # Compute the portfolio value for this week by summing the value of each ticker's holdings.
        portfolio_value = 0.0
        for ticker, shares in holdings.items():
            df = ticker_data[ticker]
            # Get the price for this ticker on or immediately after the week_date.
            df_filtered = df[df["Date"] >= week_date]
            if not df_filtered.empty:
                price = df_filtered.iloc[0]["Close"]
            else:
                price = df.iloc[-1]["Close"]  # fallback: use the most recent available price.
            portfolio_value += shares * price
        
        result.append({
            "x": week_date.strftime("%Y-%m-%d"),
            "y": round(portfolio_value, 2),
            "holdings": {ticker: round(shares, 4) for ticker, shares in holdings.items()}
        })
    
    # Return the list of 52 weekly coordinates as JSON.
    return jsonify(result)

if __name__ == '__main__':
    # For development. In production, use a proper WSGI server.
    app.run(debug=True)
