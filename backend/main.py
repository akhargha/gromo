from fastapi import FastAPI, HTTPException
import requests
import yfinance as yf
import datetime
from dateutil import parser
import uvicorn
import os
from supabase import create_client, Client

app = FastAPI()

# Set up the Supabase client using environment variables.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Missing SUPABASE_URL or SUPABASE_KEY environment variables")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/investment_chart")
def get_investment_chart():
    """
    Computes the total investment value for each week in the past 52 weeks.
    
    For each week:
      - Retrieves the S&P 500 closing price.
      - Sums the cumulative units purchased in all investments made on or before that week.
      - Computes the portfolio value as: cumulative_units * current_week_price.
    
    Returns a list of dictionaries with:
         - "week": The week (YYYY-MM-DD)
         - "cumulative_units": The total units up to that week.
         - "price_per_unit": The S&P 500 closing price for that week.
         - "portfolio_value": The computed portfolio value for that week.
    
    Additionally, the computed data is inserted into the Supabase table "portfolio"
    with the following fields:
         - date (timestamp with time zone)
         - price_per_unit (numeric(10,2))
         - units (numeric(10,4))
         
    The "portfolio_value" column is automatically generated by the database.
    """
    # 1. Determine the date range for the past 52 weeks.
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(weeks=52)
    
    # 2. Fetch weekly S&P 500 data (ticker symbol '^GSPC') using yfinance.
    try:
        sp_data = yf.download(
            "^GSPC",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval="1wk",
            progress=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching S&P 500 data: {e}")
    
    if sp_data.empty:
        raise HTTPException(status_code=500, detail="No S&P 500 data returned.")
    
    # Convert the DataFrame's index (week dates) to Python datetime objects.
    weekly_dates = sp_data.index.to_pydatetime()
    # Get the weekly closing prices (a NumPy array).
    weekly_prices = sp_data['Close'].values
    
    # 3. Retrieve the investment data from the local investments service.
    try:
        response = requests.get("http://localhost:5002/investments")
        response.raise_for_status()
        investments = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching investments: {e}")
    
    # 4. Parse each investment's date (convert to UTC, then make naive for comparison).
    for inv in investments:
        try:
            dt = parser.isoparse(inv['date'])
            inv['date'] = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format in investment data: {e}")
    
    chart_data = []
    data_to_insert = []
    
    for week_date, raw_price in zip(weekly_dates, weekly_prices):
        # Immediately convert the raw price from NumPy to a Python float.
        price = float(raw_price)
        # Sum all units purchased in investments up to (and including) this week.
        cumulative_units = sum(
            inv['units_purchased'] for inv in investments if inv['date'] <= week_date
        )
        portfolio_value = cumulative_units * price
        week_str = week_date.strftime("%Y-%m-%d")
        
        # Build the JSON response data.
        chart_data.append({
            "week": week_str,
            "cumulative_units": cumulative_units,
            "price_per_unit": price,
            "portfolio_value": portfolio_value
        })
        
        # Prepare the record for insertion into the "portfolio" table.
        data_to_insert.append({
            "date": week_date.isoformat(),  # ISO format is acceptable for timestamptz.
            "price_per_unit": round(price, 2),
            "units": round(cumulative_units, 4)
        })
    
    # 6. Insert the computed records into the Supabase table "portfolio".
    try:
        insert_response = supabase.table("portfolio").insert(data_to_insert).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data into Supabase: {e}")
    
    return chart_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
