import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from ..utils.irs_compliance import IRSCompliance


class TestIRSCompliance:
    @pytest.fixture
    def irs_compliance(self):
        return IRSCompliance()

    def test_verify_compliance_meals(self, irs_compliance):
        expense = {
            "category": "meals",
            "amount": 100.00,
            "receipt": True,
            "business_purpose": "Client meeting",
            "attendees": ["John Doe", "Jane Smith"],
        }

        result = irs_compliance.verify_compliance(expense)

        assert result["is_compliant"] is True
        assert result["compliance_score"] == 1.0
        assert result["deductible_amount"] == 50.00  # 50% deductible for meals
        assert result["within_limits"] is True

    def test_verify_compliance_missing_docs(self, irs_compliance):
        expense = {
            "category": "meals",
            "amount": 100.00,
            "receipt": True,  # Missing business_purpose and attendees
        }

        result = irs_compliance.verify_compliance(expense)

        assert result["is_compliant"] is False
        assert result["compliance_score"] < 1.0
        assert len(result["missing_documentation"]) > 0

    def test_verify_compliance_mileage(self, irs_compliance):
        expense = {
            "category": "mileage",
            "amount": 50.00,
            "date": "2023-12-01",
            "distance": "100",
            "purpose": "Client visit",
        }

        result = irs_compliance.verify_compliance(expense)

        assert result["is_compliant"] is True
        assert result["compliance_score"] == 1.0
        assert not result["missing_documentation"]

    def test_verify_compliance_over_limit(self, irs_compliance):
        expense = {
            "category": "gifts",
            "amount": 50.00,  # Over $25 limit
            "receipt": True,
            "business_purpose": "Client gift",
        }

        result = irs_compliance.verify_compliance(expense)

        assert result["within_limits"] is False
        assert result["is_compliant"] is False

    def test_generate_audit_trail(self, irs_compliance):
        expense = {
            "category": "office_supplies",
            "amount": 100.00,
            "date": "2023-12-01",
            "receipt": True,
            "business_purpose": "Office supplies",
            "additional_documentation": ["invoice"],
        }

        audit_trail = irs_compliance.generate_audit_trail(expense)

        assert audit_trail["timestamp"] == "2023-12-01"
        assert audit_trail["category"] == "office_supplies"
        assert audit_trail["documentation"]["receipt"] is True
        assert audit_trail["documentation"]["purpose"] is True
        assert "compliance_check" in audit_trail

    def test_verify_compliance_home_office(self, irs_compliance):
        expense = {
            "category": "home_office",
            "amount": 1200.00,
            "receipt": True,
            "business_purpose": "Home office deduction",
        }

        result = irs_compliance.verify_compliance(expense)

        assert result["is_compliant"] is True
        assert result["within_limits"] is True
        assert result["deductible_amount"] == 1200.00

    def test_verify_compliance_invalid_category(self, irs_compliance):
        expense = {"category": "invalid_category", "amount": 100.00}

        result = irs_compliance.verify_compliance(expense)

        assert result["compliance_score"] == 1.0  # No requirements for invalid category
        assert not result["missing_documentation"]

    def test_verify_compliance_zero_amount(self, irs_compliance):
        expense = {
            "category": "meals",
            "amount": 0.00,
            "receipt": True,
            "business_purpose": "Client meeting",
            "attendees": ["John Doe"],
        }

        result = irs_compliance.verify_compliance(expense)

        assert result["deductible_amount"] == 0.00
        assert result["within_limits"] is True

    def test_audit_trail_missing_date(self, irs_compliance):
        expense = {"category": "office_supplies", "amount": 100.00, "receipt": True}

        audit_trail = irs_compliance.generate_audit_trail(expense)

        assert audit_trail["timestamp"] is None
        assert "compliance_check" in audit_trail
