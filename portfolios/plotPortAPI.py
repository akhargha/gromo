import requests
import pandas as pd
import matplotlib.pyplot as plt

# Define the endpoint
PORTFOLIO_ENDPOINT = "http://127.0.0.1:5000/portfolio"  # Change this to the actual endpoint if needed

# Fetch data from the API
try:
    response = requests.get(PORTFOLIO_ENDPOINT)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching portfolio data: {e}")
    exit()

# Convert data to a pandas DataFrame
df = pd.DataFrame(data)
df['x'] = pd.to_datetime(df['x'])  # Convert date strings to datetime

# Plot the data
plt.figure(figsize=(12, 6))
plt.plot(df['x'], df['y'], marker='o', linestyle='-', color='b', label='Portfolio Value')
plt.xlabel("Date")
plt.ylabel("Portfolio Value ($)")
plt.title("Portfolio Value Over Time")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()