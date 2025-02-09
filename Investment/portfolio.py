from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import pandas as pd
from market_utils import get_market_data, get_portfolio_data

class PortfolioManager:
    def __init__(self, supabase):
        self.supabase = supabase
        self.portfolio_configs = [
            {
                'name': 'S&P 500 Index',
                'description': 'Tracks the S&P 500 index through VOO ETF',
                'ticker': 'VOO'
            },
            {
                'name': 'Vanguard Total Market',
                'description': 'Broad market exposure through VTI ETF',
                'ticker': 'VTI'
            },
            {
                'name': 'Nasdaq-100 Index',
                'description': 'Tech-heavy index tracking through QQQ ETF',
                'ticker': 'QQQ'
            }
        ]

    def setup_portfolios(self) -> None:
        """Initialize portfolio data with real market data"""
        for portfolio in self.portfolio_configs:
            # Get 1-year data
            data_1y = get_market_data(portfolio['ticker'], weeks=52)
            # Get 5-year data
            data_5y = get_market_data(portfolio['ticker'], weeks=260)
            
            if data_1y and data_5y:
                portfolio_data = {
                    'name': portfolio['name'],
                    'description': portfolio['description'],
                    'historical_return_1y': data_1y['historical_return_1y'],
                    'historical_return_5y': data_5y['historical_return_1y'],
                    'current_value_per_unit': data_1y['current_value_per_unit'],
                    'historical_data_1y': data_1y['historical_data_1y'],
                    'historical_data_5y': data_5y['historical_data_1y'],
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                self._update_portfolio_data(portfolio['name'], portfolio_data)

    def _update_portfolio_data(self, name: str, data: Dict) -> None:
        """Update or create portfolio data in database"""
        existing = self.supabase.table('portfolios').select('id').eq('name', name).execute()
        
        if not existing.data:
            self.supabase.table('portfolios').insert(data).execute()
        else:
            self.supabase.table('portfolios').update(data).eq('name', name).execute()

    def get_portfolio_performance(self, portfolio_id: int) -> Optional[Dict]:
        """Get portfolio performance data"""
        portfolio = self.supabase.table('portfolios').select('*').eq('id', portfolio_id).execute()
        
        if not portfolio.data:
            return None
            
        portfolio_data = portfolio.data[0]
        market_data = get_portfolio_data(portfolio_data['name'])
        
        if market_data:
            self._update_portfolio_data(portfolio_data['name'], market_data)
            portfolio_data.update(market_data)
            
        return portfolio_data

    def update_user_investment_history(
        self,
        user_investment: Dict,
        portfolio_data: Dict,
        current_time: datetime
    ) -> List[Dict]:
        """Update investment history with latest market data"""
        historical_prices = json.loads(portfolio_data['historical_data_1y'])
        total_units = float(user_investment['total_units'])
        total_invested = float(user_investment['total_invested_amount'])
        start_date = datetime.fromisoformat(user_investment['initial_investment_date'])
        
        return self.format_investment_data_points(
            total_invested,
            total_units,
            historical_prices,
            start_date
        )

    def format_investment_data_points(
        self,
        investment_amount: float,
        units: float,
        historical_prices: List[Dict],
        start_date: datetime
    ) -> List[Dict]:
        """Format investment data points for visualization"""
        data_points = []
        
        for price_point in historical_prices:
            date = datetime.fromisoformat(price_point['x'])
            if date >= start_date:
                current_value = units * float(price_point['y'])
                data_points.append({
                    'x': price_point['x'],
                    'y': round(current_value, 2),
                    'invested_amount': round(investment_amount, 2)
                })
        
        return data_points

    def update_user_investment_value(
        self,
        user_investment_id: int,
        portfolio_data: Dict
    ) -> None:
        """Update user investment with current market value"""
        response = self.supabase.table('user_investments').select('*').eq('id', user_investment_id).execute()
        if not response.data:
            return
        
        investment = response.data[0]
        current_price = float(portfolio_data['current_value_per_unit'])
        total_units = float(investment['total_units'])
        
        current_value = total_units * current_price
        growth_percentage = ((current_value - float(investment['total_invested_amount'])) 
                            / float(investment['total_invested_amount'])) * 100
        
        self.supabase.table('user_investments').update({
            'total_current_value': round(current_value, 2),
            'total_growth_percentage': round(growth_percentage, 2)
        }).eq('id', user_investment_id).execute()

    def get_user_investment_performance(self, credit_card_id: int) -> Optional[Dict]:
        """Get complete investment performance data for a user"""
        response = self.supabase.table('user_investments') \
            .select('*, portfolios(name)') \
            .eq('credit_card_id', credit_card_id) \
            .execute()

        if not response.data:
            return None

        investment = response.data[0]
        portfolio_name = investment['portfolios']['name']
        market_data = get_portfolio_data(portfolio_name)
        
        if not market_data:
            return None

        current_time = datetime.utcnow()
        data_points = self.update_user_investment_history(investment, market_data, current_time)

        # Calculate current metrics
        current_units = float(investment['total_units'])
        current_price = float(market_data['current_value_per_unit'])
        current_value = current_units * current_price
        total_invested = float(investment['total_invested_amount'])
        growth_percentage = ((current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0

        # Update investment record
        self.supabase.table('user_investments').update({
            'total_current_value': round(current_value, 2),
            'total_growth_percentage': round(growth_percentage, 2),
            'investment_data_points': json.dumps(data_points)
        }).eq('id', investment['id']).execute()

        return {
            'performance_data': data_points,
            'summary': {
                'total_invested': round(total_invested, 2),
                'current_value': round(current_value, 2),
                'growth_percentage': round(growth_percentage, 2),
                'total_units': round(current_units, 4),
                'current_price': round(current_price, 2),
                'portfolio_name': portfolio_name
            }
        }

    def update_all_investment_histories(self) -> Dict:
        """Update investment histories for all users"""
        response = self.supabase.table('user_investments').select('*, portfolios(name)').execute()
        
        updated_count = 0
        for investment in response.data:
            portfolio_name = investment['portfolios']['name']
            market_data = get_portfolio_data(portfolio_name)
            
            if market_data:
                current_time = datetime.utcnow()
                data_points = self.update_user_investment_history(investment, market_data, current_time)
                
                self.supabase.table('user_investments').update({
                    'investment_data_points': json.dumps(data_points)
                }).eq('id', investment['id']).execute()
                
                updated_count += 1

        return {
            'updated_count': updated_count,
            'total_processed': len(response.data)
        }