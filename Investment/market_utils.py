import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from functools import lru_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataError(Exception):
    """Custom exception for market data fetching errors"""
    pass

@lru_cache(maxsize=100)
def _fetch_yahoo_data(ticker: str, start_timestamp: int, end_timestamp: int, interval: str) -> Dict:
    """Fetch data from Yahoo Finance with caching"""
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
    params = {
        'period1': start_timestamp,
        'period2': end_timestamp,
        'interval': interval,
    }
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()['chart']['result'][0]
    except requests.RequestException as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        raise MarketDataError(f"Failed to fetch data for {ticker}: {str(e)}")

def get_market_data(ticker: str, weeks: int = 52) -> Optional[Dict]:
    """Fetch market data from Yahoo Finance"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)
        
        data = _fetch_yahoo_data(
            ticker,
            int(start_date.timestamp()),
            int(end_date.timestamp()),
            '1wk'
        )
        
        df = process_market_data(data)
        return format_market_data(df)
    
    except (MarketDataError, ValueError) as e:
        logger.error(f"Error in get_market_data for {ticker}: {str(e)}")
        return generate_mock_data(get_base_price(ticker))
    except Exception as e:
        logger.error(f"Unexpected error in get_market_data: {str(e)}")
        return None

def process_market_data(data: Dict) -> pd.DataFrame:
    """Process raw market data into a DataFrame"""
    timestamps = data['timestamp']
    closes = data['indicators']['quote'][0]['close']
    
    df = pd.DataFrame({
        'Date': pd.to_datetime(timestamps, unit='s'),
        'Close': closes
    })
    
    # Handle missing values
    df['Close'] = df['Close'].fillna(method='ffill')
    
    return df.dropna()

def format_market_data(df: pd.DataFrame) -> Dict:
    """Format processed market data for API response"""
    # Format historical data points
    historical_points = [
        {
            'x': date.isoformat(),
            'y': float(price)
        }
        for date, price in zip(df['Date'], df['Close'])
    ]
    
    # Calculate returns
    total_return = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]
    annual_return = ((1 + total_return) ** (52/len(df)) - 1) * 100
    
    return {
        'historical_data_1y': json.dumps(historical_points),
        'historical_return_1y': round(annual_return, 2),
        'current_value_per_unit': float(df['Close'].iloc[-1]),
        'updated_at': datetime.utcnow().isoformat()
    }

def get_portfolio_data(portfolio_name: str) -> Optional[Dict]:
    """Get market data based on portfolio type"""
    portfolio_tickers = {
        'S&P 500 Index': 'VOO',
        'Vanguard Total Market': 'VTI',
        'Nasdaq-100 Index': 'QQQ'
    }
    
    ticker = portfolio_tickers.get(portfolio_name)
    if not ticker:
        logger.error(f"Unknown portfolio name: {portfolio_name}")
        return None
    
    return get_market_data(ticker)

def calculate_growth(
    invested_amount: float,
    units: float,
    current_price: float
) -> Dict[str, float]:
    """Calculate investment growth metrics"""
    if invested_amount <= 0 or units <= 0:
        return {
            'current_value': 0.0,
            'growth_percentage': 0.0
        }
    
    current_value = units * current_price
    growth_percentage = ((current_value - invested_amount) / invested_amount) * 100
    
    return {
        'current_value': round(current_value, 2),
        'growth_percentage': round(growth_percentage, 2)
    }

def get_base_price(ticker: str) -> float:
    """Get base price for mock data generation"""
    base_prices = {
        'VOO': 400.0,
        'VTI': 220.0,
        'QQQ': 380.0
    }
    return base_prices.get(ticker, 100.0)

def generate_mock_data(base_price: float = 100.0) -> Dict:
    """Generate mock data for testing"""
    end_date = datetime.now()
    dates = [(end_date - timedelta(weeks=x)) for x in range(52)]
    dates.reverse()
    
    historical_points = []
    current_price = base_price
    
    for date in dates:
        # Add some random variation
        current_price *= (1 + (pd.np.random.random() - 0.5) * 0.02)
        historical_points.append({
            'x': date.isoformat(),
            'y': round(current_price, 2)
        })
    
    return {
        'historical_data_1y': json.dumps(historical_points),
        'historical_return_1y': 12.0,  # Mock 12% annual return
        'current_value_per_unit': round(current_price, 2),
        'updated_at': datetime.utcnow().isoformat()
    }