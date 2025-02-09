import os
import uuid
from flask import Flask, jsonify
from supabase import create_client, Client
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import logging
from flask_cors import CORS
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("REACT_APP_SUPABASE_URL"),
    os.getenv("REACT_APP_SUPABASE_ANON_KEY")
)

class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__()
        self.message = message
        self.status_code = status_code

@app.errorhandler(APIError)
def handle_exception(err):
    response = {"error": err.message}
    return jsonify(response), err.status_code

def get_sp500_historical_data():
    """
    Fetch **daily** S&P 500 historical close prices for the past 52 weeks.
    Returns a pandas Series keyed by date (datetime).
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=52)
        
        logger.info(f"Fetching daily S&P 500 data from {start_date.date()} to {end_date.date()}")

        ticker = yf.Ticker("^GSPC")
        df = ticker.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )

        if df.empty:
            raise APIError("No S&P 500 data available", 404)

        # We'll use the 'Close' column as the daily S&P 500 price
        daily_data = df["Close"].copy()

        # Drop any rows without data
        daily_data.dropna(inplace=True)

        # Remove any timezone information
        daily_data.index = daily_data.index.tz_localize(None)
        
        logger.info(f"Retrieved {len(daily_data)} days of S&P 500 data")
        logger.debug(f"Data range: {daily_data.index[0]} to {daily_data.index[-1]}")
        return daily_data
        
    except Exception as e:
        logger.error(f"Error fetching S&P 500 data: {str(e)}")
        raise APIError(f"Failed to fetch historical data: {str(e)}", 500)

def get_investments():
    """
    Get all investments from the database, validate, and return as a list of dicts:
      [
        {
          'date': datetime(...),
          'units_purchased': float,
          'amount_invested': float,
          'price_per_unit': float
        },
        ...
      ]
    """
    try:
        logger.info("Fetching investments from database")
        result = supabase.table("investments").select("*").order("date").execute()
            
        if not result.data:
            logger.warning("No investments found in database")
            return []
            
        valid_investments = []
        for inv in result.data:
            try:
                # 'date' might look like '2025-02-09T00:00:00'
                date_str = inv['date'].split('T')[0]
                investment_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                investment = {
                    'date': investment_date,
                    'units_purchased': float(inv['units_purchased']),
                    'amount_invested': float(inv['amount_invested']),
                    'price_per_unit': float(inv['price_per_unit'])
                }
                valid_investments.append(investment)
                logger.debug(f"Validated investment: {investment}")
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid investment data: {inv}, Error: {str(e)}")
                continue
                
        logger.info(f"Found {len(valid_investments)} valid investments")
        return valid_investments
        
    except Exception as e:
        logger.error(f"Error fetching investments: {str(e)}")
        raise APIError(f"Failed to fetch investments: {str(e)}", 500)

def calculate_portfolio_value(as_of_date: datetime, sp500_price: float, investments: list) -> float:
    """
    Calculate the total portfolio value on a given date, using the S&P 500 daily close price.
    This function returns 0 if no investments exist before or on as_of_date.
    """
    # Filter investments made on or before `as_of_date`
    relevant_investments = [
        inv for inv in investments 
        if inv['date'].date() <= as_of_date.date()
    ]
    if not relevant_investments:
        return 0.0

    # Total units = sum of all units purchased so far
    total_units = sum(inv['units_purchased'] for inv in relevant_investments)
    portfolio_value = total_units * sp500_price

    logger.debug(
        f"Date: {as_of_date.date()}, Price: {sp500_price:.2f}, "
        f"Units: {total_units:.4f}, Value: {portfolio_value:.2f}"
    )
    return portfolio_value

def calculate_and_sync_portfolio():
    """
    1. Fetch daily S&P 500 prices for ~52 weeks.
    2. Fetch all investments.
    3. For each day in the S&P 500 dataset, calculate the portfolio value (units * price).
    4. Sync results to 'portfolio' table, one row per day, with (id, date, price_per_unit, units).
    5. Return plot data: [ {x: date_str, y: portfolio_value}, ... ].
    """
    try:
        # 1. Get daily S&P 500 data
        sp500_prices = get_sp500_historical_data()  # pandas Series

        # 2. Get investments
        investments = get_investments()
        if not investments:
            logger.warning("No investments found, returning empty portfolio")
            return []

        logger.info("Starting daily portfolio value calculations")
        portfolio_history = []
        database_updates = []

        # 3. Iterate over each day in the S&P 500 data
        #    The index is a pandas DatetimeIndex
        for as_of_date, sp500_price in sp500_prices.items():
            value = calculate_portfolio_value(as_of_date, sp500_price, investments)

            # Prepare for chart
            portfolio_history.append({
                "x": as_of_date.strftime('%Y-%m-%d'),
                "y": round(value, 2)
            })

            # How many units do we have by this date?
            relevant_investments = [
                inv for inv in investments 
                if inv['date'].date() <= as_of_date.date()
            ]
            total_units = sum(inv['units_purchased'] for inv in relevant_investments)

            # Prepare for DB
            database_updates.append({
                "id": str(uuid.uuid4()),
                "date": as_of_date.strftime('%Y-%m-%d'),
                "price_per_unit": round(sp500_price, 2),
                "units": round(total_units, 4)
                # If your DB has a generated column for portfolio_value, it will fill automatically
            })

        # 4. Sync to database
        if database_updates:
            logger.info("Syncing portfolio data to database")
            try:
                # Clear old data
                supabase.table("portfolio").delete().neq("id", None).execute()

                # Insert new data in batches of 50
                batch_size = 50
                for i in range(0, len(database_updates), batch_size):
                    batch = database_updates[i : i + batch_size]
                    supabase.table("portfolio").insert(batch).execute()
                
                logger.info("Database sync completed successfully")
            except Exception as e:
                logger.error(f"Database sync failed: {str(e)}")

        logger.info(f"Calculated {len(portfolio_history)} days of portfolio values")
        return portfolio_history
        
    except Exception as e:
        logger.error(f"Portfolio calculation failed: {str(e)}")
        raise APIError(f"Failed to process portfolio data: {str(e)}", 500)

@app.route("/portfolio", methods=["GET"])
def get_portfolio():
    """
    Endpoint returning daily portfolio values for the past ~52 weeks.
    Shows real-dollar jumps whenever investments occur.
    """
    try:
        logger.info("Processing portfolio request")
        plot_data = calculate_and_sync_portfolio()
        
        if not plot_data:
            logger.warning("No portfolio data; returning 52 weeks of zero-value data")
            # Generate ~1 year of daily dates
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=52)
            date_range = pd.date_range(start_date, end_date, freq='D')
            zero_data = [
                {"x": d.strftime('%Y-%m-%d'), "y": 0.0}
                for d in date_range
            ]
            return jsonify(zero_data), 200
        
        logger.info(f"Returning portfolio data with {len(plot_data)} points")
        return jsonify(plot_data), 200
        
    except Exception as e:
        logger.error(f"Portfolio request failed: {str(e)}")
        raise APIError(str(e), 500)

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5003)
