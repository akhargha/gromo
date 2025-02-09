from flask import Flask, jsonify
import requests
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

def get_weekly_data(ticker):
    """Fetches one year of weekly data for the given ticker from Yahoo Finance."""
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=52)
    
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
        
        # Convert timestamps to datetime and drop any rows with missing data.
        df = pd.DataFrame({
            'Date': pd.to_datetime(timestamps, unit='s'),
            'Close': closes
        }).dropna()
        
        return df
        
    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return None

@app.route('/data', methods=['GET'])
def data_endpoint():
    """API endpoint that returns weekly x & y coordinates for each financial instrument."""
    tickers = ['VOO', 'IVV', 'SPY']
    result = {}
    
    for ticker in tickers:
        df = get_weekly_data(ticker)
        if df is not None:
            # Prepare the data as a list of coordinate dictionaries.
            data_points = [
                {'x': date.strftime('%Y-%m-%d'), 'y': close}
                for date, close in zip(df['Date'], df['Close'])
            ]
            result[ticker] = data_points
        else:
            result[ticker] = []  # or consider an error message per ticker
    
    return jsonify(result)

if __name__ == '__main__':
    # Run the Flask app. In production, use a proper WSGI server instead.
    app.run(debug=True)
