import requests
import json

BASE_URL = 'http://localhost:5000'

def test_get_portfolios():
    """
    Test GET /api/portfolios endpoint
    Checks if status == 200
    """
    print("Running test_get_portfolios()...")
    response = requests.get(f"{BASE_URL}/api/portfolios")
    if response.status_code == 200:
        print("  [✓] GET /api/portfolios => Success")
    else:
        print(f"  [x] GET /api/portfolios => Failed (status: {response.status_code})")

def test_invest():
    """
    Test POST /api/invest endpoint
    - Adjust data payload to match your DB/test scenario
    - Currently invests for a single 'cashback_transaction_id'
      or for all uninvested if you've changed the server code
    """
    print("Running test_invest()...")
    data = {
        "credit_card_id": 4,
        "portfolio_id": 1,
        "cashback_transaction_id": 15  # Adjust if you changed to "bulk invest"
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(f"{BASE_URL}/api/invest", json=data, headers=headers)

    if response.status_code == 200:
        resp_json = response.json()
        if 'error' in resp_json:
            print(f"  [x] POST /api/invest => Error reported: {resp_json['error']}")
        else:
            print("  [✓] POST /api/invest => Success")
    else:
        print(f"  [x] POST /api/invest => Failed (status: {response.status_code})")

def test_investment_status(credit_card_id=4):
    """
    Test GET /api/investment/<credit_card_id> endpoint
    Checks if status == 200 or 404
    """
    print("Running test_investment_status()...")
    response = requests.get(f"{BASE_URL}/api/investment/{credit_card_id}")
    if response.status_code == 200:
        print(f"  [✓] GET /api/investment/{credit_card_id} => Success")
    elif response.status_code == 404:
        print(f"  [x] GET /api/investment/{credit_card_id} => Not Found (404)")
    else:
        print(f"  [x] GET /api/investment/{credit_card_id} => Failed (status: {response.status_code})")

def test_investment_performance(credit_card_id=4):
    """
    Test GET /api/investment/performance/<credit_card_id> endpoint
    Checks if status == 200 or 404
    """
    print("Running test_investment_performance()...")
    response = requests.get(f"{BASE_URL}/api/investment/performance/{credit_card_id}")
    if response.status_code == 200:
        print(f"  [✓] GET /api/investment/performance/{credit_card_id} => Success")
    elif response.status_code == 404:
        print(f"  [x] GET /api/investment/performance/{credit_card_id} => Not Found (404)")
    else:
        print(f"  [x] GET /api/investment/performance/{credit_card_id} => Failed (status: {response.status_code})")

def test_update_all_investments():
    """
    Test POST /api/investment/update-all endpoint
    Checks if status == 200
    """
    print("Running test_update_all_investments()...")
    response = requests.post(f"{BASE_URL}/api/investment/update-all")
    if response.status_code == 200:
        print("  [✓] POST /api/investment/update-all => Success")
    else:
        print(f"  [x] POST /api/investment/update-all => Failed (status: {response.status_code})")

if __name__ == "__main__":
    print("Testing all investment API endpoints...\n")

    test_get_portfolios()
    test_invest()  # or adjust for 'bulk' if your code invests all at once
    test_investment_status()
    test_investment_performance()
    test_update_all_investments()

    print("\nFinished testing all endpoints.")
