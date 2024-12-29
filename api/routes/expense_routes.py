from flask import Blueprint, request, jsonify, g
from flask_paginate import Pagination, get_page_args
from api.middleware.auth_middleware import require_auth
from api.schemas.expense_schemas import expense_schema, expenses_schema, expense_update_schema
from api.services.expense_service import ExpenseService
from api.utils.error_handler import handle_api_error
from http import HTTPStatus

expense_routes = Blueprint('expenses', __name__)
expense_service = ExpenseService()

@expense_routes.route("/expenses", methods=["POST"])
@require_auth
def create_expense():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No data provided"}), HTTPStatus.BAD_REQUEST
        
        # Add user_id from authenticated user
        json_data['user_id'] = g.user.id
        
        # Validate and deserialize input
        data = expense_schema.load(json_data)
        expense = expense_service.create_expense(data)
        
        return jsonify(expense_schema.dump(expense)), HTTPStatus.CREATED

@expense_routes.route("/expenses", methods=["GET"])
@require_auth
def get_expenses():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        total, expenses = expense_service.get_expenses_paginated(g.user.id, page, per_page)
        
        return jsonify({
            'total': total,
            'items': expenses_schema.dump(expenses)
        }), HTTPStatus.OK
