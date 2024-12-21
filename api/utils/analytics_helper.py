from typing import List, Dict, Any
from datetime import datetime
import numpy as np
import logging
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from .tax_calculator import TaxCalculator

def calculate_expense_trends(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate expense trends over time"""
    df = pd.DataFrame(expenses)
    
    # Convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by month and category
    monthly_trends = df.groupby([
        df['date'].dt.to_period('M'),
        'category'
    ])['amount'].sum().unstack()
    
    # Calculate trend lines
    trends = {}
    for category in monthly_trends.columns:
        if not monthly_trends[category].empty:
            trend = calculate_trend_line(monthly_trends[category])
            trends[category] = {
                'slope': trend['slope'],
                'intercept': trend['intercept'],
                'r_squared': trend['r_squared']
            }
    
    return {
        'monthly_data': monthly_trends.to_dict(),
        'trend_analysis': trends
    }

def identify_spending_patterns(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Identify recurring spending patterns"""
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    
    patterns = {
        'weekly': analyze_weekly_patterns(df),
        'monthly': analyze_monthly_patterns(df),
        'seasonal': analyze_seasonal_patterns(df)
    }
    
    return patterns

def generate_expense_predictions(expenses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate expense predictions using historical data"""
    df = pd.DataFrame(expenses)
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by category and month
    monthly_data = df.groupby([
        df['date'].dt.to_period('M'),
        'category'
    ])['amount'].sum().unstack()
    
    predictions = {}
    for category in monthly_data.columns:
        if not monthly_data[category].empty:
            pred = predict_future_expenses(monthly_data[category])
            predictions[category] = {
                'next_month': pred['next_month'],
                'next_quarter': pred['next_quarter'],
                'confidence': pred['confidence']
            }
    
    return predictions

def calculate_trend_line(data: pd.Series) -> Dict[str, float]:
    """Calculate trend line parameters"""
    X = np.arange(len(data)).reshape(-1, 1)
    y = data.values.reshape(-1, 1)
    
    model = LinearRegression()
    model.fit(X, y)
    
    return {
        'slope': float(model.coef_[0]),
        'intercept': float(model.intercept_),
        'r_squared': model.score(X, y)
    }

def analyze_weekly_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze weekly spending patterns"""
    weekly_patterns = df.groupby([
        df['date'].dt.day_name(),
        'category'
    ])['amount'].agg(['mean', 'std']).to_dict()
    
    return weekly_patterns

def analyze_monthly_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze monthly spending patterns"""
    monthly_patterns = df.groupby([
        df['date'].dt.month,
        'category'
    ])['amount'].agg(['mean', 'std']).to_dict()
    
    return monthly_patterns

def analyze_seasonal_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze seasonal spending patterns"""
    df['quarter'] = df['date'].dt.quarter
    seasonal_patterns = df.groupby([
        'quarter',
        'category'
    ])['amount'].agg(['mean', 'std']).to_dict()
    
    return seasonal_patterns

def predict_future_expenses(data: pd.Series) -> Dict[str, Any]:
    """Predict future expenses using time series analysis"""
    # Simple moving average prediction
    window = 3
    moving_avg = data.rolling(window=window).mean()
    
    last_value = moving_avg.iloc[-1]
    trend = (moving_avg.iloc[-1] - moving_avg.iloc[-2]) if len(moving_avg) > 1 else 0
    
    predictions = {
        'next_month': float(last_value + trend),
        'next_quarter': float(last_value + 3 * trend),
        'confidence': calculate_prediction_confidence(data)
    }
    
    return predictions

def calculate_prediction_confidence(data: pd.Series) -> float:
    """Calculate confidence score for predictions"""
    # Simple confidence calculation based on data consistency
    if len(data) < 2:
        return 0.0
        
    std = data.std()
    mean = data.mean()
    
    if mean == 0:
        return 0.0
        
    coefficient_of_variation = std / mean
    confidence = 1 / (1 + coefficient_of_variation)
    
    return float(confidence)

def generate_analytics_summary(
    trends: Dict[str, Any],
    patterns: Dict[str, Any],
    predictions: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate summary of analytics findings"""
    summary = {
        'trend_summary': summarize_trends(trends),
        'pattern_insights': summarize_patterns(patterns),
        'prediction_highlights': summarize_predictions(predictions)
    }
    
    return summary

def summarize_trends(trends: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize key trends"""
    trend_summary = {
        'increasing_categories': [],
        'decreasing_categories': [],
        'stable_categories': []
    }
    
    for category, trend in trends.get('trend_analysis', {}).items():
        if trend['slope'] > 0.05:
            trend_summary['increasing_categories'].append(category)
        elif trend['slope'] < -0.05:
            trend_summary['decreasing_categories'].append(category)
        else:
            trend_summary['stable_categories'].append(category)
    
    return trend_summary

def summarize_patterns(patterns: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize key patterns"""
    return {
        'weekly_highlights': extract_pattern_highlights(patterns.get('weekly', {})),
        'monthly_highlights': extract_pattern_highlights(patterns.get('monthly', {})),
        'seasonal_highlights': extract_pattern_highlights(patterns.get('seasonal', {}))
    }

def summarize_predictions(predictions: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize key predictions"""
    return {
        'highest_predicted_increase': find_highest_prediction(predictions),
        'most_consistent_category': find_most_consistent_category(predictions),
        'categories_to_watch': identify_categories_to_watch(predictions)
    }

def extract_pattern_highlights(pattern_data: Dict[str, Any]) -> List[str]:
    """Extract key highlights from pattern data"""
    highlights = []
    for key, value in pattern_data.items():
        if isinstance(value, dict) and 'mean' in value and value['mean'] > 0:
            highlights.append(f"Average {key}: {value['mean']:.2f}")
    return highlights

def find_highest_prediction(predictions: Dict[str, Any]) -> Dict[str, Any]:
    """Find category with highest predicted increase"""
    max_increase = {'category': None, 'increase': 0}
    
    for category, pred in predictions.items():
        if pred['next_month'] > max_increase['increase']:
            max_increase = {
                'category': category,
                'increase': pred['next_month']
            }
    
    return max_increase

def find_most_consistent_category(predictions: Dict[str, Any]) -> str:
    """Find most consistent category based on prediction confidence"""
    return max(
        predictions.items(),
        key=lambda x: x[1]['confidence']
    )[0]

def identify_categories_to_watch(predictions: Dict[str, Any]) -> List[str]:
    """Identify categories with significant predicted changes"""
    to_watch = []
    
    for category, pred in predictions.items():
        if abs(pred['next_month'] - pred['next_quarter']/3) > 0.1:
            to_watch.append(category)
    
    return to_watch

def analyze_optimization_opportunities(user_id: int, year: int = None) -> List[Dict[str, Any]]:
    """Analyze potential tax optimization opportunities"""
    try:
        expenses = get_user_expenses(user_id, year)
        calculator = TaxCalculator()
        
        opportunities = []
        for expense in expenses:
            # Analyze each expense for optimization potential
            optimization = {
                'expense': expense,
                'potential_savings': calculator.calculate_tax_savings(
                    Decimal(str(expense['amount']))
                ),
                'suggestion': generate_optimization_suggestion(expense)
            }
            opportunities.append(optimization)
            
        return opportunities
    except Exception as e:
        logging.error(f"Error analyzing optimization opportunities: {e}")
        return []
