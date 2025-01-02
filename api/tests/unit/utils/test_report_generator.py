import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from api.utils.report_generator import ReportGenerator


@pytest.fixture
def report_generator():
    return ReportGenerator()


@pytest.fixture
def mock_database():
    with patch("api.utils.report_generator.get_db_connection") as mock:
        yield mock


@pytest.fixture
def sample_expenses():
    return [
        {"category": "fuel", "total": 200.0},
        {"category": "maintenance", "total": 300.0},
    ]


def test_generate_expense_summary_success(
    report_generator, mock_database, sample_expenses
):
    """Test successful expense summary generation"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = sample_expenses
    mock_database.return_value.cursor.return_value = mock_cursor

    result = report_generator.generate_expense_summary(
        user_id=1, start_date="2023-01-01", end_date="2023-12-31"
    )

    assert result["total_expenses"] == 500.0
    assert len(result["by_category"]) == 2
    assert result["by_category"]["fuel"]["amount"] == 200.0
    assert result["by_category"]["maintenance"]["amount"] == 300.0


def test_generate_quarterly_report_success(report_generator, mock_database):
    """Test successful quarterly report generation"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [{"category": "fuel", "total": 200.0}]
    mock_cursor.fetchone.return_value = {"total": 1000.0}
    mock_database.return_value.cursor.return_value = mock_cursor

    result = report_generator.generate_quarterly_report(user_id=1, year=2023, quarter=1)

    assert result["income"] == 1000.0
    assert "expenses" in result
    assert result["quarter"] == 1
    assert result["year"] == 2023


def test_export_to_csv_success(report_generator):
    """Test successful CSV export"""
    data = {"category": ["fuel", "maintenance"], "amount": [200.0, 300.0]}

    csv_content = report_generator.export_to_csv(data)

    assert isinstance(csv_content, str)
    assert "category,amount" in csv_content
    assert "fuel,200.0" in csv_content


def test_generate_tax_summary_success(report_generator, mock_database):
    """Test successful tax summary generation"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = {"total": 5000.0}
    mock_cursor.fetchall.return_value = [{"category": "business", "total": 1000.0}]
    mock_database.return_value.cursor.return_value = mock_cursor

    result = report_generator.generate_tax_summary(user_id=1, year=2023)

    assert result["total_income"] == 5000.0
    assert "total_deductions" in result
    assert "taxable_income" in result
    assert "estimated_tax" in result


def test_generate_schedule_c_success(report_generator, mock_database):
    """Test successful Schedule C generation"""
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = {"total": 5000.0}
    mock_cursor.fetchall.return_value = [
        {"category": "business_expense", "total": 1000.0}
    ]
    mock_database.return_value.cursor.return_value = mock_cursor

    result = report_generator.generate_schedule_c(user_id=1, year=2023)

    assert result["gross_income"] == 5000.0
    assert "expenses" in result
    assert "total_expenses" in result
    assert "net_profit" in result


def test_generate_custom_report_success(report_generator, mock_database):
    """Test successful custom report generation"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        {
            "date": "2023-01-01",
            "category": "fuel",
            "description": "Gas",
            "amount": 50.0,
            "is_business": True,
        }
    ]
    mock_database.return_value.cursor.return_value = mock_cursor

    result = report_generator.generate_custom_report(
        user_id=1,
        start_date="2023-01-01",
        end_date="2023-12-31",
        categories=["fuel"],
        report_type="summary",
    )

    assert "total_expenses" in result
    assert "by_category" in result
    assert "business_expenses" in result


def test_generate_analytics_success(report_generator, mock_database):
    """Test successful analytics generation"""
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = [
        {"month": "01", "category": "fuel", "total": 200.0}
    ]
    mock_database.return_value.cursor.return_value = mock_cursor

    result = report_generator.generate_analytics(user_id=1, year=2023)

    assert "monthly_trends" in result
    assert "category_trends" in result
    assert "year_over_year" in result
