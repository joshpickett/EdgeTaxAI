from marshmallow import Schema, fields, validate
from .base_schemas import AuditSchema
from api.models.deductions import DeductionType


class DeductionSchema(AuditSchema):
    type = fields.Enum(DeductionType, required=True)
    description = fields.String(required=True, validate=validate.Length(max=500))
    amount = fields.Decimal(required=True, places=2)
    calculated_amount = fields.Decimal(dump_only=True, places=2)
    tax_year = fields.Integer(required=True)
    user_id = fields.Integer(required=True)
    document_id = fields.Integer(allow_none=True)
    expense_id = fields.Integer(allow_none=True)
    category = fields.String(validate=validate.Length(max=100))
    is_verified = fields.Boolean(default=False)


deduction_schema = DeductionSchema()
deductions_schema = DeductionSchema(many=True)
