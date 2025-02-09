from fastapi import FastAPI, HTTPException
import requests
import yfinance as yf
import datetime
from dateutil import parser
import uvicorn

app = FastAPI()

@app.get("/investment_chart")
def get_investment_chart():
    """
    Computes the total investment value for each week in the past 52 weeks.
    
    For each week:
      - Retrieve the S&P 500 closing price.
      - Sum the units purchased in all investments that were made on or before that week.
      - Multiply the cumulative units by the current week's closing price.
      
    Returns:
      A list of dictionaries with:
         - "week": The week (YYYY-MM-DD)
         - "total_value": The cumulative investment value at that week.
         - "price_per_share": The S&P 500 closing price for that week.
    
    Example:
      With weekly prices:
         week1: $10, week2: $11, week3: $15, week4: $20
      And two investments:
         - 1 unit purchased during week1
         - 1 unit purchased during week3
      The computed data would be:
         week1: 1 * 10  = $10
         week2: 1 * 11  = $11
         week3: 2 * 15  = $30
         week4: 2 * 20  = $40
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

    # Convert the DataFrame's index (which contains the week dates) to Python datetime objects.
    weekly_dates = sp_data.index.to_pydatetime()
    # Use the 'Close' price as the weekly price.
    weekly_prices = sp_data['Close'].values

    # 3. Retrieve the investment data from the local investments service.
    try:
        response = requests.get("http://localhost:5002/investments")
        response.raise_for_status()
        investments = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching investments: {e}")

    # 4. Parse each investment's date from its ISO format into a datetime object.
    #    Convert the date to UTC and then remove the timezone info so it becomes naive.
    for inv in investments:
        try:
            dt = parser.isoparse(inv['date'])
            inv['date'] = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format in investment data: {e}")

    # 5. For each week, compute the total value of investments up to that date.
    #    For every week, sum all `units_purchased` for investments where inv['date'] <= week_date,
    #    then compute the total value as: total_value = cumulative_units * current_week_price.
    chart_data = []
    for week_date, price in zip(weekly_dates, weekly_prices):
        total_units = sum(
            inv['units_purchased'] for inv in investments if inv['date'] <= week_date
        )
        total_value = total_units * price
        chart_data.append({
            "week": week_date.strftime("%Y-%m-%d"),
            "total_value": float(total_value),
            "price_per_share": float(price)
        })

    return chart_data

if __name__ == "__main__":
    # Run the FastAPI app using uvicorn on port 8001.
    uvicorn.run(app, host="0.0.0.0", port=8001)
