from marshmallow import Schema, fields, validate
from api.models.expenses import ExpenseCategory
from .base_schemas import AuditSchema
from .document_schemas import DocumentSchema


class ExpenseSchema(AuditSchema):
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    category = fields.Enum(ExpenseCategory, required=True)
    date = fields.Date(required=True)
    user_id = fields.Integer(required=True)
    receipt_url = fields.String(validate=validate.Length(max=512))
    transaction_id = fields.String(validate=validate.Length(max=100))
    document_id = fields.Integer(allow_none=True)
    tax_year = fields.Integer()
    is_deductible = fields.Boolean(default=False)
    document = fields.Nested(DocumentSchema, dump_only=True)


class ExpenseUpdateSchema(ExpenseSchema):
    amount = fields.Float(validate=validate.Range(min=0))
    description = fields.String(validate=validate.Length(min=1, max=500))
    category = fields.Enum(ExpenseCategory)
    date = fields.Date()
    user_id = fields.Integer()


expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)
expense_update_schema = ExpenseUpdateSchema()
