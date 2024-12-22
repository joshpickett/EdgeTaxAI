from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional, Union
from ..utils.db_utils import get_db_connection
from ..utils.error_handler import handle_api_error
from ..utils.report_generator import ReportGenerator
from ..utils.tax_calculator import TaxCalculator
import pandas as pd
import io

reports_bp = Blueprint('reports', __name__)
report_generator = ReportGenerator()
tax_calculator = TaxCalculator()

@reports_bp.route("/reports/tax-summary", methods=["POST"])
def generate_tax_summary():
    """Generate comprehensive tax summary with expense analysis"""
    try:
        data = request.json
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        include_projections = data.get('include_projections', False)

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        summary = report_generator.generate_tax_summary(user_id, start_date, end_date, include_projections)
        return jsonify(summary)
    except Exception as e:
        logging.error(f"Error generating tax summary: {e}")
        return handle_api_error(e)

@reports_bp.route("/reports/quarterly-tax", methods=["POST"])
def generate_quarterly_summary():
    """Generate quarterly expense and tax summary"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        quarter = data.get('quarter')

        # Calculate quarterly tax estimates
        quarterly_summary = report_generator.generate_quarterly_report(
            user_id, year, quarter
        )
        
        # Add tax calculations
        tax_estimates = tax_calculator.calculate_quarterly_tax(
            quarterly_summary['income'],
            quarterly_summary['expenses']
        )
        
        return jsonify({
            **quarterly_summary,
            'tax_estimates': tax_estimates
        }), 200

    except Exception as e:
        logging.error(f"Error generating quarterly summary: {e}")
        return handle_api_error(e)

@reports_bp.route("/tax-summary", methods=["POST"])
def generate_tax_summary():
    """Generate tax summary report"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        summary = report_generator.generate_tax_summary(user_id, year)
        return jsonify(summary)
        
    except Exception as e:
        logging.error(f"Error generating tax summary: {e}")
        return handle_api_error(e)

@reports_bp.route("/irs/schedule-c", methods=["POST"])
def generate_schedule_c():
    """Generate IRS Schedule C report"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        schedule_c = report_generator.generate_schedule_c(user_id, year)
        return jsonify(schedule_c)
    except Exception as e:
        logging.error(f"Error generating Schedule C: {e}")
        return handle_api_error(e)

@reports_bp.route("/custom-report", methods=["POST"])
def generate_custom_report():
    """Generate custom report based on user specifications"""
    try:
        data = request.json
        user_id = data.get('user_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        categories = data.get('categories', [])
        report_type = data.get('report_type', 'detailed')
        format_type = data.get('format', 'json')
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        report = report_generator.generate_custom_report(
            user_id, 
            start_date, 
            end_date,
            categories,
            report_type
        )
        
        if format_type == 'csv':
            csv_data = report_generator.export_to_csv(report)
            return send_file(
                io.StringIO(csv_data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'custom_report_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        
        return jsonify(report)
    except Exception as e:
        logging.error(f"Error generating custom report: {e}")
        return handle_api_error(e)

@reports_bp.route("/analytics", methods=["POST"])
def generate_analytics():
    """Generate expense pattern analytics"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        analytics = report_generator.generate_analytics(user_id, year)
        return jsonify(analytics)
    except Exception as e:
        logging.error(f"Error generating analytics: {e}")
        return handle_api_error(e)

@reports_bp.route("/tax-savings", methods=["POST"])
def analyze_tax_savings():
    """Analyze potential tax saving opportunities"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        savings = report_generator.analyze_tax_savings(user_id, year)
        return jsonify(savings)
    except Exception as e:
        logging.error(f"Error analyzing tax savings: {e}")
        return handle_api_error(e)

@reports_bp.route("/export", methods=["POST"])
def export_report():
    """Export report in specified format (PDF, Excel, JSON)"""
    try:
        data = request.json
        user_id = data.get('user_id')
        report_type = data.get('report_type')
        format_type = data.get('format', 'pdf')
        
        if not user_id or not report_type:
            return jsonify({"error": "User ID and report type are required"}), 400
            
        # Generate report data
        report_data = report_generator.generate_report(user_id, report_type)
        
        # Export based on format
        if format_type == 'pdf':
            return export_pdf(report_data)
        elif format_type == 'excel':
            return export_excel(report_data)
        elif format_type == 'json':
            return export_json(report_data)
        else:
            return jsonify({"error": "Unsupported format"}), 400
            
    except Exception as e:
        logging.error(f"Error exporting report: {e}")
        return handle_api_error(e)

def export_pdf(data: Dict[str, Any]) -> Union[send_file, tuple]:
    """Generate PDF report"""
    try:
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        
        # Add report title
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 800, "Tax Report")
        
        # Add report data
        y_position = 750
        pdf.setFont("Helvetica", 12)
        for key, value in data.items():
            pdf.drawString(50, y_position, f"{key}: {value}")
            y_position -= 20
            
        pdf.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'tax_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    except Exception as e:
        logging.error(f"PDF generation error: {e}")
        return jsonify({"error": "Failed to generate PDF"}), 500

def export_excel(data: Dict[str, Any]) -> Union[send_file, tuple]:
    """Generate Excel report"""
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Tax Report"
        
        # Add headers
        headers = list(data.keys())
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
            
        # Add data
        for col, value in enumerate(data.values(), 1):
            ws.cell(row=2, column=col, value=value)
            
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'tax_report_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
    except Exception as e:
        logging.error(f"Excel generation error: {e}")
        return jsonify({"error": "Failed to generate Excel file"}), 500

def export_json(data: Dict[str, Any]) -> Union[send_file, tuple]:
    """Generate JSON report"""
    try:
        return jsonify(data)
    except Exception as e:
        logging.error(f"JSON generation error: {e}")
        return jsonify({"error": "Failed to generate JSON"}), 500

@reports_bp.route("/advanced-analytics", methods=["POST"])
def generate_advanced_analytics():
    """Generate advanced analytics with trend analysis and predictions"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        # Get historical data
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Analyze expense trends
        cursor.execute("""
            SELECT category, amount, date
            FROM expenses
            WHERE user_id = ?
            ORDER BY date
        """, (user_id,))
        
        expenses = cursor.fetchall()
        
        # Calculate trends and patterns
        trends = calculate_expense_trends(expenses)
        patterns = identify_spending_patterns(expenses)
        predictions = generate_expense_predictions(expenses)
        
        analytics = {
            'trends': trends,
            'patterns': patterns,
            'predictions': predictions,
            'summary': generate_analytics_summary(trends, patterns, predictions)
        }
        
        return jsonify(analytics)
    except Exception as e:
        logging.error(f"Error generating advanced analytics: {e}")
        return handle_api_error(e)

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

if __name__ == "__main__":
    reports_page()
