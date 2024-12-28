import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from datetime import datetime, timedelta
from typing import Dict, Any
from http import HTTPStatus
import logging
from flask import Blueprint, request, jsonify
from flask_paginate import Pagination, get_page_args
from api.middleware.auth_middleware import require_auth
from api.services.expense_service import ExpenseService
from api.utils.validators import validate_expense
from api.utils.error_handler import handle_api_error
from api.utils.report_generator import ReportGenerator
from api.utils.rate_limit import rate_limit
from api.utils.cache_utils import CacheManager, cache_response

expense_blueprint = Blueprint('expense', __name__)
report_generator = ReportGenerator()
expense_service = ExpenseService()
cache_manager = CacheManager()

@expense_blueprint.route('/expenses/summary', methods=['GET'])
@require_auth
@rate_limit("100/hour")
@cache_response(timeout=300)
def get_expense_summary():
    """
    Get expense summary with tax implications
    ---
    parameters:
      - name: user_id
        in: query
        type: string
        required: true
      - name: start_date
        in: query
        type: string
        format: date
        required: false
      - name: end_date
        in: query
        type: string
        format: date
        required: false
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id is required"}), HTTPStatus.BAD_REQUEST
            
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        summary = report_generator.generate_expense_summary(user_id, start_date, end_date)
        return jsonify(summary), HTTPStatus.OK
    except Exception as e:
        return handle_api_error(e)

@expense_blueprint.route('/expenses', methods=['POST'])
@require_auth
@rate_limit("100/hour")
def create_expense():
    """
    Create a new expense
    ---
    parameters:
      - name: expense
        in: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
            description:
              type: string
            category:
              type: string
            date:
              type: string
              format: date
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), HTTPStatus.BAD_REQUEST

        validation_result = validate_expense(data)
        if validation_result is not True:
            return jsonify({"error": validation_result}), HTTPStatus.BAD_REQUEST

        result = expense_service.handle_expense(data)
        return jsonify(result), HTTPStatus.CREATED
    except Exception as e:
        return handle_api_error(e)

@expense_blueprint.route('/expenses/<expense_id>', methods=['GET'])
@require_auth
@rate_limit("100/hour")
def get_expense(expense_id: str):
    """
    Get a specific expense by ID
    ---
    parameters:
      - name: expense_id
        in: path
        type: string
        required: true
    """
    try:
        result = expense_service.get_expense(expense_id)
        if not result:
            return jsonify({"error": "Expense not found"}), HTTPStatus.NOT_FOUND
        return jsonify(result), HTTPStatus.OK
    except Exception as e:
        return handle_api_error(e)

@expense_blueprint.route('/expenses/<expense_id>', methods=['DELETE'])
@require_auth
@rate_limit("100/hour")
def delete_expense(expense_id: str):
    """
    Delete a specific expense
    ---
    parameters:
      - name: expense_id
        in: path
        type: string
        required: true
    """
    try:
        result = expense_service.delete_expense(expense_id)
        if not result:
            return jsonify({"error": "Expense not found"}), HTTPStatus.NOT_FOUND
        return jsonify({"message": "Expense deleted successfully"}), HTTPStatus.OK
    except Exception as e:
        return handle_api_error(e)

@expense_blueprint.route('/expenses/<expense_id>', methods=['PUT'])
@require_auth
@rate_limit("100/hour")
def update_expense(expense_id: str):
    """
    Update an existing expense
    ---
    parameters:
      - name: expense_id
        in: path
        type: string
        required: true
      - name: expense
        in: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
            description:
              type: string
            category:
              type: string
            date:
              type: string
              format: date
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), HTTPStatus.BAD_REQUEST

        validation_result = validate_expense(data)
        if validation_result is not True:
            return jsonify({"error": validation_result}), HTTPStatus.BAD_REQUEST

        result = expense_service.update_expense(expense_id, data)
        if not result:
            return jsonify({"error": "Expense not found"}), HTTPStatus.NOT_FOUND
        return jsonify(result), HTTPStatus.OK
    except Exception as e:
        return handle_api_error(e)

@expense_blueprint.route('/expenses', methods=['GET'])
@require_auth
@rate_limit("100/hour")
def get_expenses():
    """
    Get all expenses with pagination
    ---
    parameters:
      - name: page
        in: query
        type: integer
        required: false
      - name: per_page
        in: query
        type: integer
        required: false
      - name: user_id
        in: query
        type: string
        required: true
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id is required"}), HTTPStatus.BAD_REQUEST

        page, per_page, offset = get_page_args(
            page_parameter='page',
            per_page_parameter='per_page'
        )
        per_page = min(per_page or 20, 100)  # Limit maximum items per page

        total, expenses = expense_service.get_expenses_paginated(
            user_id, 
            page=page,
            per_page=per_page
        )

        pagination = Pagination(
            page=page,
            per_page=per_page,
            total=total,
            css_framework='bootstrap4'
        )

        return jsonify({
            'expenses': expenses,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), HTTPStatus.OK
    except Exception as e:
        return handle_api_error(e)
