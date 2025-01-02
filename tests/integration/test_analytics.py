import pytest
from datetime import datetime, timedelta
from api.utils.analytics_integration import AnalyticsIntegration


@pytest.fixture
def analytics():
    return AnalyticsIntegration()


def test_unified_report_generation(analytics):
    """Test unified report generation"""
    user_id = 1
    report = analytics.generate_unified_report(user_id)

    assert "patterns" in report
    assert "insights" in report
    assert "recommendations" in report
    assert "timestamp" in report


def test_pattern_analysis(analytics):
    """Test pattern analysis"""
    patterns = analytics._analyze_patterns(
        {
            "expenses": [
                {"amount": 100, "category": "food"},
                {"amount": 200, "category": "transport"},
            ]
        }
    )

    assert "expense_patterns" in patterns
    assert "by_category" in patterns["expense_patterns"]


def test_insight_generation(analytics):
    """Test insight generation"""
    patterns = {
        "expense_patterns": {
            "by_category": {
                "food": {"amount": 100, "percentage": 20, "trend": "increasing"}
            }
        }
    }

    insights = analytics._generate_insights(patterns)
    assert len(insights) > 0
    assert insights[0]["type"] == "expense_pattern"


def test_recommendation_generation(analytics):
    """Test recommendation generation"""
    insights = [
        {"type": "tax_opportunity", "category": "transport", "potential_savings": 100}
    ]

    recommendations = analytics._generate_recommendations(insights)
    assert len(recommendations) > 0
    assert "action" in recommendations[0]
