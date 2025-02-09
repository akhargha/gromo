import requests
import json

BASE_URL = 'http://localhost:5000'

def test_get_portfolios():
    """Test GET /api/portfolios endpoint"""
    response = requests.get(f'{BASE_URL}/api/portfolios')
    print("\nGET /api/portfolios:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_invest():
    """Test POST /api/invest endpoint"""
    data = {
        "credit_card_id": 4,
        "portfolio_id": 1,
        "cashback_transaction_id": 15
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f'{BASE_URL}/api/invest',
        json=data,  # This automatically handles JSON encoding
        headers=headers
    )
    
    print("\nPOST /api/invest:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_investment_status(credit_card_id=4):
    """Test GET /api/investment/<credit_card_id> endpoint"""
    response = requests.get(f'{BASE_URL}/api/investment/{credit_card_id}')
    print(f"\nGET /api/investment/{credit_card_id}:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_investment_performance(credit_card_id=4):
    """Test GET /api/investment/performance/<credit_card_id> endpoint"""
    response = requests.get(f'{BASE_URL}/api/investment/performance/{credit_card_id}')
    print(f"\nGET /api/investment/performance/{credit_card_id}:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("Testing Investment API endpoints...")
    
    # Test each endpoint
    test_get_portfolios()
    test_invest()
    test_investment_status()
    test_investment_performance()