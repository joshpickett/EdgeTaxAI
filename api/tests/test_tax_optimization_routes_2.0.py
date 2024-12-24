import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from ..routes.tax_optimization_routes import tax_optimization_bp
from ..utils.shared_tax_service import TaxService

@pytest.fixture
def app():
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(tax_optimization_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_tax_service():
    with patch('api.utils.shared_tax_service.TaxService') as mock:
        yield mock

class TestTaxOptimizationRoutes:
    def test_optimize_tax_strategy_success(self, client, mock_tax_service):
        mock_tax_service.return_value.calculate_tax_savings.return_value = Decimal('1000.00')

        response = client.post('/tax/optimize',
                             json={
                                 'user_id': 123,
                                 'year': 2023
                             })
        
        assert response.status_code == 200
        assert 'optimization_suggestions' in response.json

    def test_analyze_deductions_success(self, client, mock_tax_service):
        mock_tax_service.return_value.calculate_tax_savings.return_value = Decimal('500.00')

        response = client.post('/analyze-deductions',
                             json={
                                 'user_id': 123,
                                 'year': 2023
                             })
        
        assert response.status_code == 200
        data = response.json
        assert 'optimization_suggestions' in data
        assert 'potential_savings' in data
        assert 'recommended_actions' in data

    def test_enhanced_analyze_success(self, client, mock_tax_service):
        mock_tax_service.return_value.analyze_tax_context.return_value = {
            'potential_deductions': 1000.00,
            'suggestions': ['Suggestion 1', 'Suggestion 2']
        }

        response = client.post('/enhanced-analyze',
                             json={
                                 'user_id': 123,
                                 'quarter': 1,
                                 'expense_data': {
                                     'category': 'office_supplies',
                                     'amount': 500.00
                                 }
                             })
        
        assert response.status_code == 200
        data = response.json
        assert 'optimization_suggestions' in data
        assert 'potential_savings' in data

    def test_missing_required_fields(self, client):
        response = client.post('/enhanced-analyze',
                             json={
                                 'quarter': 1  # Missing user_id
                             })
        
        assert response.status_code == 400
        assert 'error' in response.json

    def test_invalid_quarter(self, client):
        response = client.post('/enhanced-analyze',
                             json={
                                 'user_id': 123,
                                 'quarter': 5,  # Invalid quarter
                                 'expense_data': {}
                             })
        
        assert response.status_code == 400
        assert 'error' in response.json

    def test_optimization_suggestions_quality(self, client, mock_tax_service):
        mock_suggestions = {
            'potential_deductions': 1000.00,
            'suggestions': [
                {
                    'category': 'home_office',
                    'potential_savings': 500.00,
                    'confidence': 0.9,
                    'description': 'Detailed suggestion'
                }
            ]
        }
        mock_tax_service.return_value.analyze_tax_context.return_value = mock_suggestions

        response = client.post('/enhanced-analyze',
                             json={
                                 'user_id': 123,
                                 'quarter': 1,
                                 'expense_data': {}
                             })
        
        assert response.status_code == 200
        suggestions = response.json['optimization_suggestions']
        assert len(suggestions) > 0
        assert 'confidence' in suggestions[0]
        assert suggestions[0]['confidence'] > 0.8

    def test_tax_savings_calculation_accuracy(self, client, mock_tax_service):
        test_cases = [
            (1000.00, 150.00),  # 15% tax rate
            (5000.00, 1100.00),  # 22% tax rate
            (10000.00, 2400.00)  # 24% tax rate
        ]

        for income, expected_savings in test_cases:
            mock_tax_service.return_value.calculate_tax_savings.return_value = Decimal(str(expected_savings))

            response = client.post('/tax/optimize',
                                 json={
                                     'user_id': 123,
                                     'year': 2023,
                                     'income': income
                                 })
            
            assert response.status_code == 200
            assert abs(float(response.json['optimization_suggestions']['potential_savings']) - expected_savings) < 0.01

    def test_deduction_validation(self, client):
        invalid_deductions = [
            {'category': 'meals', 'amount': 100000.00},  # Unreasonably high
            {'category': 'invalid_category', 'amount': 100.00},  # Invalid category
            {'category': 'home_office', 'amount': -100.00}  # Negative amount
        ]

        for deduction in invalid_deductions:
            response = client.post('/analyze-deductions',
                                 json={
                                     'user_id': 123,
                                     'year': 2023,
                                     'deductions': [deduction]
                                 })
            
            assert response.status_code == 400
            assert 'error' in response.json

    def test_optimization_strategy_prioritization(self, client, mock_tax_service):
        mock_strategies = {
            'potential_deductions': 2000.00,
            'suggestions': [
                {
                    'category': 'home_office',
                    'potential_savings': 1000.00,
                    'priority': 'high'
                },
                {
                    'category': 'supplies',
                    'potential_savings': 500.00,
                    'priority': 'medium'
                },
                {
                    'category': 'misc',
                    'potential_savings': 100.00,
                    'priority': 'low'
                }
            ]
        }
        mock_tax_service.return_value.analyze_tax_context.return_value = mock_strategies

        response = client.post('/enhanced-analyze',
                             json={
                                 'user_id': 123,
                                 'quarter': 1,
                                 'expense_data': {}
                             })
        
        assert response.status_code == 200
        suggestions = response.json['optimization_suggestions']
        
        # Verify suggestions are ordered by priority
        priorities = [s['priority'] for s in suggestions]
        assert priorities == ['high', 'medium', 'low']
        
        # Verify savings amounts are reasonable
        assert suggestions[0]['potential_savings'] > suggestions[1]['potential_savings']

    def test_quarterly_optimization_analysis(self, client, mock_tax_service):
        mock_tax_service.return_value.analyze_tax_context.return_value = {
            'potential_deductions': 1000.00,
            'quarterly_breakdown': {
                'Q1': {'deductions': 250.00, 'suggestions': ['Suggestion 1']},
                'Q2': {'deductions': 250.00, 'suggestions': ['Suggestion 2']},
                'Q3': {'deductions': 250.00, 'suggestions': ['Suggestion 3']},
                'Q4': {'deductions': 250.00, 'suggestions': ['Suggestion 4']}
            }
        }

        response = client.post('/enhanced-analyze',
                             json={
                                 'user_id': 123,
                                 'quarter': 1,
                                 'expense_data': {}
                             })
        
        assert response.status_code == 200
        assert 'quarterly_breakdown' in response.json
        assert len(response.json['quarterly_breakdown']) == 4
        
        # Verify each quarter has suggestions
        for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            assert quarter in response.json['quarterly_breakdown']
            assert 'suggestions' in response.json['quarterly_breakdown'][quarter]

    def test_optimization_with_historical_data(self, client, mock_tax_service):
        historical_data = {
            'previous_year': {
                'deductions': 10000.00,
                'effective_rate': 0.22,
                'optimization_score': 0.85
            },
            'current_year': {
                'deductions': 12000.00,
                'effective_rate': 0.20,
                'optimization_score': 0.90
            }
        }
        
        mock_tax_service.return_value.get_historical_data.return_value = historical_data
        mock_tax_service.return_value.analyze_tax_context.return_value = {
            'potential_deductions': 2000.00,
            'suggestions': ['Suggestion 1'],
            'historical_comparison': {
                'improvement': 0.05,
                'trending': 'positive'
            }
        }

        response = client.post('/tax/optimize',
                             json={
                                 'user_id': 123,
                                 'year': 2023,
                                 'include_historical': True
                             })
        
        assert response.status_code == 200
        assert 'historical_comparison' in response.json
        assert response.json['historical_comparison']['trending'] == 'positive'
        assert response.json['historical_comparison']['improvement'] > 0

    def test_category_specific_optimization(self, client, mock_tax_service):
        categories = ['home_office', 'vehicle_expenses', 'supplies', 'professional_services']
        
        for category in categories:
            mock_tax_service.return_value.analyze_category_optimization.return_value = {
                'category': category,
                'current_deductions': 1000.00,
                'potential_deductions': 1500.00,
                'specific_suggestions': [
                    'Category specific suggestion 1',
                    'Category specific suggestion 2'
                ]
            }

            response = client.post('/analyze-deductions',
                                 json={
                                     'user_id': 123,
                                     'year': 2023,
                                     'category': category
                                 })
            
            assert response.status_code == 200
            assert response.json['category'] == category
            assert 'specific_suggestions' in response.json
            assert len(response.json['specific_suggestions']) > 0
            assert response.json['potential_deductions'] > response.json['current_deductions']

    def test_optimization_confidence_scores(self, client, mock_tax_service):
        mock_tax_service.return_value.analyze_tax_context.return_value = {
            'potential_deductions': 1000.00,
            'suggestions': [
                {
                    'description': 'High confidence suggestion',
                    'confidence_score': 0.95,
                    'potential_savings': 500.00
                },
                {
                    'description': 'Medium confidence suggestion',
                    'confidence_score': 0.75,
                    'potential_savings': 300.00
                },
                {
                    'description': 'Low confidence suggestion',
                    'confidence_score': 0.45,
                    'potential_savings': 200.00
                }
            ]
        }

        response = client.post('/enhanced-analyze',
                             json={
                                 'user_id': 123,
                                 'quarter': 1,
                                 'expense_data': {}
                             })
        
        assert response.status_code == 200
        suggestions = response.json['optimization_suggestions']
        
        # Verify suggestions are ordered by confidence score
        confidence_scores = [s['confidence_score'] for s in suggestions]
        assert confidence_scores == sorted(confidence_scores, reverse=True)
        
        # Verify high confidence suggestions have higher potential savings
        assert suggestions[0]['potential_savings'] > suggestions[-1]['potential_savings']

    def test_risk_assessment(self, client, mock_tax_service):
        mock_tax_service.return_value.analyze_tax_context.return_value = {
            'potential_deductions': 1000.00,
            'suggestions': [
                {
                    'description': 'Safe suggestion',
                    'risk_level': 'low',
                    'potential_savings': 300.00
                },
                {
                    'description': 'Moderate risk suggestion',
                    'risk_level': 'medium',
                    'potential_savings': 500.00
                },
                {
                    'description': 'High risk suggestion',
                    'risk_level': 'high',
                    'potential_savings': 1000.00
                }
            ]
        }

        response = client.post('/enhanced-analyze',
                             json={
                                 'user_id': 123,
                                 'quarter': 1,
                                 'expense_data': {}
                             })
        
        assert response.status_code == 200
        suggestions = response.json['optimization_suggestions']
        
        # Verify each suggestion has a risk assessment
        for suggestion in suggestions:
            assert 'risk_level' in suggestion
            assert suggestion['risk_level'] in ['low', 'medium', 'high']
            
        # Verify higher risk suggestions have higher potential savings
        risk_levels = [s['risk_level'] for s in suggestions]
        savings = [s['potential_savings'] for s in suggestions]
        assert risk_levels.index('high') == savings.index(max(savings))
