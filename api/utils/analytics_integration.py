import logging
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
from .db_utils import get_db_connection
from .ai_utils import analyze_patterns
from .tax_calculator import TaxCalculator

class AnalyticsIntegration:
    def __init__(self):
        self.conn = get_db_connection()
        self.tax_calculator = TaxCalculator()
        
    def generate_unified_report(self, user_id: int) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            # Gather data from all sources
            expenses = self._fetch_expenses(user_id)
            bank_data = self._fetch_bank_data(user_id)
            gig_data = self._fetch_gig_data(user_id)
            tax_data = self._fetch_tax_data(user_id)
            
            # Analyze patterns
            patterns = analyze_patterns({
                'expenses': expenses,
                'bank_data': bank_data,
                'gig_data': gig_data,
                'tax_data': tax_data
            })
            
            # Generate insights
            insights = self._generate_insights(patterns)
            
            return {
                'patterns': patterns,
                'insights': insights,
                'recommendations': self._generate_recommendations(insights),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Error generating unified report: {e}")
            return {}
            
    def _fetch_expenses(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch expense data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM expenses 
            WHERE user_id = ? 
            ORDER BY date DESC
        """, (user_id,))
        return cursor.fetchall()
        
    def _fetch_bank_data(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch bank transaction data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM bank_transactions 
            WHERE user_id = ? 
            ORDER BY date DESC
        """, (user_id,))
        return cursor.fetchall()
        
    def _fetch_gig_data(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch gig platform data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM gig_earnings 
            WHERE user_id = ? 
            ORDER BY date DESC
        """, (user_id,))
        return cursor.fetchall()
        
    def _fetch_tax_data(self, user_id: int) -> Dict[str, Any]:
        """Fetch tax-related data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tax_estimates 
            WHERE user_id = ? 
            ORDER BY date DESC
        """, (user_id,))
        return cursor.fetchall()
        
    def _generate_insights(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from patterns"""
        insights = []
        
        # Analyze expense patterns
        if 'expense_patterns' in patterns:
            insights.extend(self._analyze_expense_patterns(patterns['expense_patterns']))
            
        # Analyze income patterns
        if 'income_patterns' in patterns:
            insights.extend(self._analyze_income_patterns(patterns['income_patterns']))
            
        # Analyze tax implications
        if 'tax_patterns' in patterns:
            insights.extend(self._analyze_tax_patterns(patterns['tax_patterns']))
            
        return insights
        
    def _generate_recommendations(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for insight in insights:
            if insight['type'] == 'expense_pattern':
                recommendations.extend(self._get_expense_recommendations(insight))
            elif insight['type'] == 'tax_opportunity':
                recommendations.extend(self._get_tax_recommendations(insight))
            elif insight['type'] == 'income_pattern':
                recommendations.extend(self._get_income_recommendations(insight))
                
        return recommendations
        
    def _analyze_expense_patterns(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze expense patterns for insights"""
        insights = []
        
        # Analyze category distribution
        category_dist = pd.DataFrame(patterns['by_category'])
        top_categories = category_dist.nlargest(3, 'amount')
        
        for _, category in top_categories.iterrows():
            insights.append({
                'type': 'expense_pattern',
                'category': category.name,
                'amount': category['amount'],
                'percentage': category['percentage'],
                'trend': category['trend']
            })
            
        return insights
        
    def _analyze_income_patterns(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze income patterns for insights"""
        insights = []
        
        # Analyze income sources
        for source, data in patterns['by_source'].items():
            insights.append({
                'type': 'income_pattern',
                'source': source,
                'amount': data['amount'],
                'frequency': data['frequency'],
                'stability': data['stability']
            })
            
        return insights
        
    def _analyze_tax_patterns(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze tax patterns for insights"""
        insights = []
        
        # Analyze deduction opportunities
        for category, data in patterns['deductions'].items():
            if data['potential_savings'] > 0:
                insights.append({
                    'type': 'tax_opportunity',
                    'category': category,
                    'potential_savings': data['potential_savings'],
                    'confidence': data['confidence']
                })
                
        return insights
