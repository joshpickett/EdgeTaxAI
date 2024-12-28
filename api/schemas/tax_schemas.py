from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
from decimal import Decimal

class QuarterlyTaxSchema(Schema):
    user_id = fields.Int(required=True)
    income = fields.Decimal(required=True)
    expenses = fields.Decimal(required=True)
    quarter = fields.Int(required=True, validate=validate.Range(min=1, max=4))
    year = fields.Int(missing=lambda: datetime.now().year)

    @validates('income')
    def validate_income(self, value):
        if value < 0:
            raise ValidationError('Income must be non-negative')

class TaxSavingsSchema(Schema):
    user_id = fields.Int(required=True)
    amount = fields.Decimal(required=True)
    
    @validates('amount')
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError('Amount must be positive')

class DeductionAnalysisSchema(Schema):
    user_id = fields.Int(required=True)
    expenses = fields.List(fields.Dict(), required=True)
    year = fields.Int(missing=lambda: datetime.now().year)

    @validates('expenses')
    def validate_expenses(self, value):
        if not value:
            raise ValidationError('Expenses list cannot be empty')

class TaxDocumentSchema(Schema):
    user_id = fields.Int(required=True)
    document_type = fields.Str(required=True, 
                             validate=validate.OneOf(['schedule_c', 'quarterly_estimate']))
    year = fields.Int(missing=lambda: datetime.now().year)
    format = fields.Str(missing='pdf', 
                       validate=validate.OneOf(['pdf', 'excel', 'json']))
