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
    """
    Invest ALL uninvested cashback transactions for a given credit_card_id and portfolio_id.
    """
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

        logger.info(f"Received investment request (bulk): {data}")

        # Validate required fields (remove cashback_transaction_id requirement)
        required_fields = ['credit_card_id', 'portfolio_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields: credit_card_id, portfolio_id'}), 400

        # Convert IDs to integers
        try:
            credit_card_id = int(data['credit_card_id'])
            portfolio_id = int(data['portfolio_id'])
        except ValueError:
            return jsonify({'error': 'Invalid ID format - must be integers'}), 400

        # ------------------------------------------------------------------------------
        # 1. Get all transactions for this credit_card_id
        # ------------------------------------------------------------------------------
        transactions_response = supabase.table('transactions') \
            .select('id') \
            .eq('credit_card_id', credit_card_id) \
            .execute()

        if not transactions_response.data:
            return jsonify({'message': 'No transactions found for this credit card ID'}), 200

        transaction_ids = [t['id'] for t in transactions_response.data]

        # ------------------------------------------------------------------------------
        # 2. Get all cashback_transactions for those transaction_ids
        #    that are NOT yet invested (no row in investment_transactions).
        # ------------------------------------------------------------------------------
        # Get all cashback transactions linked to the transaction_ids
        cb_response = supabase.table('cashback_transactions') \
            .select('id, cashback_amount, transaction_id') \
            .in_('transaction_id', transaction_ids) \
            .execute()

        if not cb_response.data:
            return jsonify({'message': 'No cashback transactions found to invest'}), 200

        # Collect all cashback_transaction_ids from the set above
        all_cb_ids = [cb['id'] for cb in cb_response.data]

        # Find which ones are already invested (exist in investment_transactions)
        invested_response = supabase.table('investment_transactions') \
            .select('cashback_transaction_id') \
            .in_('cashback_transaction_id', all_cb_ids) \
            .execute()

        invested_ids = [ir['cashback_transaction_id'] for ir in invested_response.data]

        # Filter out the ones that are already invested
        uninvested_cashbacks = [
            cb for cb in cb_response.data
            if cb['id'] not in invested_ids
        ]

        if not uninvested_cashbacks:
            return jsonify({'message': 'All cashback transactions are already invested'}), 200

        # ------------------------------------------------------------------------------
        # 3. For each uninvested cashback, perform the investment logic
        # ------------------------------------------------------------------------------
        # Get portfolio data
        portfolio = supabase.table('portfolios') \
            .select('*') \
            .eq('id', portfolio_id) \
            .execute()

        if not portfolio.data:
            return jsonify({'error': 'Portfolio not found'}), 404

        portfolio_data = portfolio.data[0]
        current_price = float(portfolio_data['current_value_per_unit'])

        # Get or create user_investment
        current_time = datetime.utcnow().isoformat()
        user_investment_response = supabase.table('user_investments') \
            .select('*') \
            .eq('credit_card_id', credit_card_id) \
            .execute()

        # If user_investment doesn't exist, create a blank one, then update as we go
        if not user_investment_response.data:
            investment_data = {
                'credit_card_id': credit_card_id,
                'portfolio_id': portfolio_id,
                'initial_investment_date': current_time,
                'total_invested_amount': 0,
                'total_units': 0,
                'total_current_value': 0,
                'total_growth_percentage': 0,
                'investment_data_points': json.dumps([]),
                'last_investment_date': current_time
            }
            
            new_investment = supabase.table('user_investments') \
                .insert(investment_data) \
                .execute()

            user_investment = new_investment.data[0]
            investment_id = user_investment['id']
        else:
            user_investment = user_investment_response.data[0]
            investment_id = user_investment['id']

        # We'll track total amounts for the final response
        total_invested_now = 0.0
        total_units_purchased = 0.0
        investment_transactions_records = []

        # Convert existing user_investment numeric values
        current_total_invested = float(user_investment['total_invested_amount'])
        current_total_units = float(user_investment['total_units'])

        # Load existing data points
        data_points = []
        if user_investment['investment_data_points']:
            try:
                data_points = json.loads(user_investment['investment_data_points'])
            except json.JSONDecodeError:
                data_points = []

        # Loop through each uninvested cashback and invest
        for cb in uninvested_cashbacks:
            cb_amount = float(cb['cashback_amount'])
            units_purchased = 0.0
            if current_price > 0:
                units_purchased = cb_amount / current_price

            # Update aggregate counters
            current_total_invested += cb_amount
            current_total_units += units_purchased
            total_invested_now += cb_amount
            total_units_purchased += units_purchased

            # Insert the single investment_transactions record
            transaction_data = {
                'user_investment_id': investment_id,
                'cashback_transaction_id': cb['id'],
                'amount_invested': cb_amount,
                'units_purchased': units_purchased,
                'price_per_unit': current_price,
                'investment_date': current_time
            }
            investment_transactions_records.append(transaction_data)

        # Now that we have the updated totals:
        # Recalculate growth
        from market_utils import calculate_growth
        growth = calculate_growth(current_total_invested, current_total_units, current_price)

        # Add a new data point reflecting the new total
        data_points.append({
            'x': current_time,
            'y': growth['current_value'],
            'invested_amount': current_total_invested
        })

        # Update user_investments
        update_data = {
            'total_invested_amount': current_total_invested,
            'total_units': current_total_units,
            'total_current_value': growth['current_value'],
            'total_growth_percentage': growth['growth_percentage'],
            'investment_data_points': json.dumps(data_points),
            'last_investment_date': current_time
        }
        supabase.table('user_investments') \
            .update(update_data) \
            .eq('id', investment_id) \
            .execute()

        # Insert all new investment_transactions in one go 
        # (or you can loop, but one .insert([...]) is typically more efficient).
        supabase.table('investment_transactions') \
            .insert(investment_transactions_records) \
            .execute()

        # ------------------------------------------------------------------------------
        # Return a summary response
        # ------------------------------------------------------------------------------
        return jsonify({
            'message': f'Successfully invested {len(uninvested_cashbacks)} cashback transactions',
            'total_amount_invested': round(total_invested_now, 2),
            'total_units_purchased': round(total_units_purchased, 4),
            'current_price_per_unit': current_price,
            'new_investment_value': growth['current_value'],
            'growth_percentage': growth['growth_percentage']
        })

    except Exception as e:
        logger.error(f"Error in invest_cashback (bulk): {str(e)}")
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