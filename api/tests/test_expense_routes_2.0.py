import pytest
from unittest.mock import patch, Mock
from flask import Flask, json
from ..routes.expense_routes import expense_blueprint
from ..shared.services.expense_service import ExpenseService


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(expense_blueprint)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestExpenseRoutes:
    @pytest.fixture
    def mock_expense_service(self):
        with patch("api.routes.expense_routes.ExpenseService") as mock:
            yield mock

    def test_get_expense_summary_success(self, client):
        response = client.get(
            "/expenses/summary?user_id=123&start_date=2023-01-01&end_date=2023-12-31"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "summary" in data

    def test_get_expense_summary_missing_user_id(self, client):
        response = client.get("/expenses/summary")
        assert response.status_code == 400
        assert b"user_id is required" in response.data

    def test_create_expense_success(self, client, mock_expense_service):
        data = {
            "description": "Test Expense",
            "amount": 100.00,
            "category": "Office Supplies",
            "date": "2023-12-01",
        }
        response = client.post(
            "/expenses", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["description"] == data["description"]

    def test_create_expense_invalid_data(self, client):
        data = {
            "description": "",  # Invalid: empty description
            "amount": -100.00,  # Invalid: negative amount
        }
        response = client.post(
            "/expenses", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 400
        assert b"validation errors" in response.data

    def test_create_expense_with_receipt(self, client, mock_expense_service):
        data = {
            "description": "Test Expense",
            "amount": 100.00,
            "category": "Office Supplies",
            "receipt_url": "http://example.com/receipt.jpg",
        }
        response = client.post(
            "/expenses", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert "receipt_url" in response_data

    @patch("api.routes.expense_routes.categorize_expense")
    def test_expense_categorization(self, mock_categorize, client):
        mock_categorize.return_value = "Office Supplies"
        data = {"description": "Printer paper", "amount": 50.00}
        response = client.post(
            "/expenses", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["category"] == "Office Supplies"

    def test_expense_tax_deduction_calculation(self, client):
        data = {"description": "Business lunch", "amount": 100.00, "category": "Meals"}
        response = client.post(
            "/expenses", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert "tax_deductible" in response_data
        assert "deduction_amount" in response_data

    @patch("api.routes.expense_routes.analyze_expense_patterns")
    def test_expense_pattern_analysis(self, mock_analyze, client):
        mock_analyze.return_value = {"frequency": "monthly", "average_amount": 100.00}
        response = client.get("/expenses/analysis?user_id=123")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "frequency" in data
        assert "average_amount" in data

    def test_bulk_expense_creation(self, client):
        data = {
            "expenses": [
                {"description": "Expense 1", "amount": 100.00},
                {"description": "Expense 2", "amount": 200.00},
            ]
        }
        response = client.post(
            "/expenses/bulk", data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert len(response_data["created_expenses"]) == 2

    def test_expense_validation_rules(self, client):
        # Test various validation rules
        invalid_cases = [
            {"amount": -100},  # Negative amount
            {"amount": "not_a_number"},  # Invalid amount type
            {"date": "invalid_date"},  # Invalid date format
            {"category": 123},  # Invalid category type
        ]

        for invalid_data in invalid_cases:
            response = client.post(
                "/expenses",
                data=json.dumps(invalid_data),
                content_type="application/json",
            )
            assert response.status_code == 400

    def test_expense_search_and_filter(self, client):
        # Test search and filter functionality
        filters = {
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "category": "Office Supplies",
            "min_amount": 50,
            "max_amount": 200,
        }
        response = client.get("/expenses/search", query_string=filters)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "expenses" in data
        assert isinstance(data["expenses"], list)

    def test_expense_summary_calculations(self, client):
        # Test summary calculations
        response = client.get("/expenses/summary?user_id=123&year=2023")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_expenses" in data
        assert "total_deductible" in data
        assert "by_category" in data
        assert "monthly_breakdown" in data

    @patch("api.routes.expense_routes.ExpenseService")
    def test_expense_sync(self, mock_service, client):
        mock_service.sync_expenses.return_value = {"synced": 10, "conflicts": 0}
        response = client.post(
            "/expenses/sync",
            data=json.dumps({"user_id": 123}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["synced"] == 10
        assert data["conflicts"] == 0

    def test_expense_export(self, client):
        # Test expense export functionality
        export_params = {
            "user_id": 123,
            "format": "csv",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        }
        response = client.get("/expenses/export", query_string=export_params)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv"
        assert "attachment" in response.headers["Content-Disposition"]

    def test_expense_categories_validation(self, client):
        # Test category validation
        invalid_category = {
            "description": "Test Expense",
            "amount": 100.00,
            "category": "InvalidCategory",
        }
        response = client.post(
            "/expenses",
            data=json.dumps(invalid_category),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert b"Invalid category" in response.data

    def test_expense_date_validation(self, client):
        # Test date validation
        future_date = {
            "description": "Test Expense",
            "amount": 100.00,
            "date": "2025-01-01",  # Future date
        }
        response = client.post(
            "/expenses", data=json.dumps(future_date), content_type="application/json"
        )
        assert response.status_code == 400
        assert b"Date cannot be in the future" in response.data

    def test_expense_amount_precision(self, client):
        # Test amount precision handling
        amount_precision = {
            "description": "Test Expense",
            "amount": 100.999,  # More than 2 decimal places
        }
        response = client.post(
            "/expenses",
            data=json.dumps(amount_precision),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert b"Amount cannot have more than 2 decimal places" in response.data

    def test_expense_deletion(self, client):
        # Test expense deletion
        response = client.delete("/expenses/123")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["message"] == "Expense deleted successfully"

        # Verify deletion
        response = client.get("/expenses/123")
        assert response.status_code == 404

    def test_expense_update(self, client):
        # Test expense update
        update_data = {"description": "Updated Description", "amount": 150.00}
        response = client.put(
            "/expenses/123",
            data=json.dumps(update_data),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["description"] == update_data["description"]
        assert data["amount"] == update_data["amount"]
