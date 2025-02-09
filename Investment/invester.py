from flask import Flask, request, jsonify
from supabase_client import supabase
from market_utils import calculate_growth
from portfolio import PortfolioManager
from datetime import datetime
import json
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
portfolio_manager = None

def init_app():
    """Initialize the application and setup portfolios"""
    global portfolio_manager
    if portfolio_manager is None:
        portfolio_manager = PortfolioManager(supabase)
        try:
            portfolio_manager.setup_portfolios()
            logger.info("Portfolio manager initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing portfolio manager: {str(e)}")
            raise

@app.before_request
def before_request():
    """Ensure portfolio manager is initialized before each request"""
    if portfolio_manager is None:
        init_app()

@app.route('/api/portfolios', methods=['GET'])
def get_portfolios():
    """Get all available portfolios with their performance data"""
    try:
        response = supabase.table('portfolios').select('*').execute()
        portfolios = response.data

        for portfolio in portfolios:
            portfolio_data = portfolio_manager.get_portfolio_performance(portfolio['id'])
            if portfolio_data:
                update_data = {
                    'historical_return_1y': portfolio_data['historical_return_1y'],
                    'current_value_per_unit': portfolio_data['current_value_per_unit'],
                    'historical_data_1y': portfolio_data['historical_data_1y'],
                    'updated_at': datetime.utcnow().isoformat()
                }
                portfolio.update(update_data)
                
                if 'historical_data_1y' in portfolio:
                    portfolio['historical_data_1y'] = json.loads(portfolio['historical_data_1y'])
                if 'historical_data_5y' in portfolio and portfolio['historical_data_5y']:
                    portfolio['historical_data_5y'] = json.loads(portfolio['historical_data_5y'])

        return jsonify(portfolios)
    except Exception as e:
        logger.error(f"Error in get_portfolios: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/invest', methods=['POST'])
def invest_cashback():
    """Invest cashback into selected portfolio"""
    try:
        # Parse JSON data from request
        if not request.is_json:
            logger.error("Request Content-Type is not application/json")
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        try:
            data = request.get_json(force=True)
        except Exception as e:
            logger.error(f"Failed to parse JSON: {str(e)}")
            return jsonify({'error': 'Invalid JSON format'}), 400

        logger.info(f"Received investment request: {data}")

        # Validate required fields
        required_fields = ['credit_card_id', 'portfolio_id', 'cashback_transaction_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Convert IDs to integers
        try:
            credit_card_id = int(data['credit_card_id'])
            portfolio_id = int(data['portfolio_id'])
            cashback_transaction_id = int(data['cashback_transaction_id'])
        except ValueError:
            return jsonify({'error': 'Invalid ID format - must be integers'}), 400

        # Check if cashback already invested
        existing = supabase.table('investment_transactions') \
            .select('id') \
            .eq('cashback_transaction_id', cashback_transaction_id) \
            .execute()
            
        if existing.data:
            return jsonify({'error': 'Cashback already invested'}), 400

        # Get cashback amount
        cashback = supabase.table('cashback_transactions') \
            .select('cashback_amount') \
            .eq('id', cashback_transaction_id) \
            .execute()
            
        if not cashback.data:
            return jsonify({'error': 'Invalid cashback transaction'}), 404

        cashback_amount = float(cashback.data[0]['cashback_amount'])

        # Get portfolio data
        portfolio = supabase.table('portfolios') \
            .select('*') \
            .eq('id', portfolio_id) \
            .execute()
            
        if not portfolio.data:
            return jsonify({'error': 'Portfolio not found'}), 404

        portfolio_data = portfolio.data[0]
        current_price = float(portfolio_data['current_value_per_unit'])
        units_purchased = cashback_amount / current_price

        # Get or create user investment
        user_investment = supabase.table('user_investments') \
            .select('*') \
            .eq('credit_card_id', credit_card_id) \
            .execute()

        current_time = datetime.utcnow().isoformat()

        if not user_investment.data:
            # Create new investment
            investment_data = {
                'credit_card_id': credit_card_id,
                'portfolio_id': portfolio_id,
                'initial_investment_date': current_time,
                'total_invested_amount': cashback_amount,
                'total_units': units_purchased,
                'total_current_value': cashback_amount,
                'total_growth_percentage': 0,
                'investment_data_points': json.dumps([{
                    'x': current_time,
                    'y': cashback_amount,
                    'invested_amount': cashback_amount
                }]),
                'last_investment_date': current_time
            }
            
            new_investment = supabase.table('user_investments') \
                .insert(investment_data) \
                .execute()
            investment_id = new_investment.data[0]['id']
        else:
            # Update existing investment
            existing = user_investment.data[0]
            new_total_invested = float(existing['total_invested_amount']) + cashback_amount
            new_total_units = float(existing['total_units']) + units_purchased
            
            growth = calculate_growth(new_total_invested, new_total_units, current_price)
            
            data_points = json.loads(existing['investment_data_points'] or '[]')
            data_points.append({
                'x': current_time,
                'y': growth['current_value'],
                'invested_amount': new_total_invested
            })

            update_data = {
                'total_invested_amount': new_total_invested,
                'total_units': new_total_units,
                'total_current_value': growth['current_value'],
                'total_growth_percentage': growth['growth_percentage'],
                'investment_data_points': json.dumps(data_points),
                'last_investment_date': current_time
            }
            
            supabase.table('user_investments') \
                .update(update_data) \
                .eq('id', existing['id']) \
                .execute()
            investment_id = existing['id']

        # Record investment transaction
        transaction_data = {
            'user_investment_id': investment_id,
            'cashback_transaction_id': cashback_transaction_id,
            'amount_invested': cashback_amount,
            'units_purchased': units_purchased,
            'price_per_unit': current_price,
            'investment_date': current_time
        }
        
        supabase.table('investment_transactions') \
            .insert(transaction_data) \
            .execute()

        return jsonify({
            'message': 'Investment successful',
            'amount_invested': cashback_amount,
            'units_purchased': units_purchased,
            'current_value': cashback_amount,
            'price_per_unit': current_price
        })

    except Exception as e:
        logger.error(f"Error in invest_cashback: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/investment/<int:credit_card_id>', methods=['GET'])
def get_investment_status(credit_card_id):
    """Get current investment status and history"""
    try:
        response = supabase.table('user_investments') \
            .select('*, portfolios(name)') \
            .eq('credit_card_id', credit_card_id) \
            .execute()

        if not response.data:
            return jsonify({'error': 'No investment found'}), 404

        investment = response.data[0]
        portfolio_name = investment['portfolios']['name']
        
        # Get latest market data
        market_data = portfolio_manager.get_portfolio_performance(investment['portfolio_id'])
        if market_data:
            current_price = float(market_data['current_value_per_unit'])
            growth = calculate_growth(
                float(investment['total_invested_amount']),
                float(investment['total_units']),
                current_price
            )
            
            # Update current value and growth
            supabase.table('user_investments') \
                .update({
                    'total_current_value': growth['current_value'],
                    'total_growth_percentage': growth['growth_percentage']
                }) \
                .eq('id', investment['id']) \
                .execute()
                
            investment['total_current_value'] = growth['current_value']
            investment['total_growth_percentage'] = growth['growth_percentage']

        # Parse investment history
        investment_history = investment['investment_data_points']
        if isinstance(investment_history, str):
            try:
                investment_history = json.loads(investment_history)
            except json.JSONDecodeError:
                investment_history = []
        elif investment_history is None:
            investment_history = []

        return jsonify({
            'portfolio_name': portfolio_name,
            'total_invested': float(investment['total_invested_amount']),
            'total_units': float(investment['total_units']),
            'current_value': float(investment['total_current_value']),
            'growth_percentage': float(investment['total_growth_percentage']),
            'investment_history': investment_history,
            'last_investment_date': investment['last_investment_date']
        })

    except Exception as e:
        logger.error(f"Error in get_investment_status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/investment/performance/<int:credit_card_id>', methods=['GET'])
def get_investment_performance(credit_card_id):
    """Get detailed investment performance data for visualization"""
    try:
        performance_data = portfolio_manager.get_user_investment_performance(credit_card_id)
        if not performance_data:
            return jsonify({'error': 'No investment found'}), 404

        return jsonify(performance_data)
    except Exception as e:
        logger.error(f"Error in get_investment_performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/investment/update-all', methods=['POST'])
def update_all_investments():
    """Update all user investment histories with latest market data"""
    try:
        result = portfolio_manager.update_all_investment_histories()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in update_all_investments: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_app()  # Initialize on startup
    app.run(debug=True)