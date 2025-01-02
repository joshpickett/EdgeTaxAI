import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from api.utils.analytics_helper import AnalyticsHelper
from api.utils.db_utils import Database


@pytest.fixture
def mock_database():
    """Create a mock database instance"""
    return Mock(spec=Database)


@pytest.fixture
def analytics_helper(mock_database):
    """Create an AnalyticsHelper instance with a mock database"""
    return AnalyticsHelper(mock_database)


@pytest.fixture
def sample_earnings_data():
    """Sample earnings data for testing"""
    return [
        {"platform": "uber", "total_amount": 1000.50, "transaction_count": 50},
        {"platform": "lyft", "total_amount": 750.25, "transaction_count": 35},
    ]


@pytest.fixture
def sample_expenses_data():
    """Sample expenses data for testing"""
    return [
        {"category": "fuel", "total_amount": 200.00, "count": 10},
        {"category": "maintenance", "total_amount": 300.00, "count": 5},
    ]


def test_get_earnings_summary_success(
    analytics_helper, mock_database, sample_earnings_data
):
    """Test successful earnings summary generation"""
    # Setup mock database response
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_earnings_data
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor

    # Test without period
    result = analytics_helper.get_earnings_summary(user_id=1)

    assert result["total_earnings"] == 1750.75  # Sum of all earnings
    assert len(result["platform_breakdown"]) == 2
    assert result["average_per_transaction"] == pytest.approx(
        20.60, 0.01
    )  # 1750.75 / 85

    # Verify platform specific data
    uber_data = next(p for p in result["platform_breakdown"] if p["platform"] == "uber")
    assert uber_data["amount"] == 1000.50
    assert uber_data["percentage"] == pytest.approx(57.15, 0.01)
    assert uber_data["transaction_count"] == 50


def test_get_earnings_summary_with_period(
    analytics_helper, mock_database, sample_earnings_data
):
    """Test earnings summary with date period"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_earnings_data
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor

    period = (datetime.now() - timedelta(days=30), datetime.now())
    result = analytics_helper.get_earnings_summary(user_id=1, period=period)

    assert result["total_earnings"] == 1750.75
    assert len(result["platform_breakdown"]) == 2


def test_get_earnings_summary_empty_data(analytics_helper, mock_database):
    """Test earnings summary with no data"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = []
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor

    result = analytics_helper.get_earnings_summary(user_id=1)

    assert result["total_earnings"] == 0
    assert len(result["platform_breakdown"]) == 0
    assert result["average_per_transaction"] == 0


def test_get_expense_analysis_success(
    analytics_helper, mock_database, sample_expenses_data
):
    """Test successful expense analysis"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_expenses_data
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor

    result = analytics_helper.get_expense_analysis(user_id=1)

    assert result["total_expenses"] == 500.00
    assert len(result["category_breakdown"]) == 2
    assert result["average_per_category"] == 250.00

    # Verify category specific data
    fuel_data = next(c for c in result["category_breakdown"] if c["category"] == "fuel")
    assert fuel_data["amount"] == 200.00
    assert fuel_data["percentage"] == 40.00
    assert fuel_data["transaction_count"] == 10


def test_get_expense_analysis_with_period(
    analytics_helper, mock_database, sample_expenses_data
):
    """Test expense analysis with date period"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_expenses_data
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor

    period = (datetime.now() - timedelta(days=30), datetime.now())
    result = analytics_helper.get_expense_analysis(user_id=1, period=period)

    assert result["total_expenses"] == 500.00
    assert len(result["category_breakdown"]) == 2


def test_get_expense_analysis_empty_data(analytics_helper, mock_database):
    """Test expense analysis with no data"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = []
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor

    result = analytics_helper.get_expense_analysis(user_id=1)

    assert result["total_expenses"] == 0
    assert len(result["category_breakdown"]) == 0
    assert result["average_per_category"] == 0


@patch("api.utils.analytics_helper.TripAnalyzer")
@patch("api.utils.analytics_helper.TaxCalculator")
def test_get_comprehensive_report(
    mock_tax_calculator,
    mock_trip_analyzer,
    analytics_helper,
    mock_database,
    sample_earnings_data,
    sample_expenses_data,
):
    """Test comprehensive report generation"""
    # Setup mocks
    mock_cursor = Mock()
    mock_cursor.fetchall.side_effect = [sample_earnings_data, sample_expenses_data]
    mock_database.get_cursor.return_value.__enter__.return_value = mock_cursor

    mock_trip_analyzer.return_value.analyze_trip_patterns.return_value = {
        "total_miles": 1000
    }

    mock_tax_calculator.return_value.get_tax_summary.return_value = {
        "estimated_tax": 300.00
    }

    result = analytics_helper.get_comprehensive_report(user_id=1)

    assert "earnings_summary" in result
    assert "expense_analysis" in result
    assert "trip_analysis" in result
    assert "tax_summary" in result
    assert result["net_income"] == 1250.75  # 1750.75 - 500.00
    assert result["profit_margin"] == pytest.approx(71.44, 0.01)


def test_get_comprehensive_report_error_handling(analytics_helper, mock_database):
    """Test error handling in comprehensive report generation"""
    mock_database.get_cursor.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        analytics_helper.get_comprehensive_report(user_id=1)

    assert "Database error" in str(exc_info.value)
