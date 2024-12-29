from marshmallow import Schema, fields, validate
from api.models.expenses import ExpenseCategory

class ExpenseSchema(Schema):
    id = fields.Integer(dump_only=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    category = fields.Enum(ExpenseCategory, required=True)
    date = fields.Date(required=True)
    user_id = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ExpenseUpdateSchema(ExpenseSchema):
    amount = fields.Float(validate=validate.Range(min=0))
    description = fields.String(validate=validate.Length(min=1, max=500))
    category = fields.Enum(ExpenseCategory)
    date = fields.Date()
    user_id = fields.Integer()

expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)
expense_update_schema = ExpenseUpdateSchema()
