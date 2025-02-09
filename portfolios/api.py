import requests
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt




def get_weekly_data(ticker):
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
        
        return pd.DataFrame({
            'Date': pd.to_datetime(timestamps, unit='s'),
            'Close': closes
        }).dropna()
        
    except Exception as e:
        print(f"Error fetching {ticker}: {str(e)}")
        return None

# Example usage for VOO, IVV, and SPY
for ticker in ['VOO', 'IVV', 'SPY']:
    df = get_weekly_data(ticker)
    if df is not None:
        print(f"\n{ticker} Weekly Data:")
        print(df.tail())


def plot_data(df, ticker):
    plt.figure(figsize=(12,6))
    plt.plot(df['Date'], df['Close'], label=ticker)
    plt.title(f'{ticker} Weekly Closing Prices')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example plot generation
voo_data = get_weekly_data('VOO')
if voo_data is not None:
    plot_data(voo_data, 'VOO')