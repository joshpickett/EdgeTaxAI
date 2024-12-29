from marshmallow import Schema, fields, validate
from api.models.bank_accounts import BankAccountType
from datetime import datetime

class BankAccountBaseSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(required=True)
    account_number = fields.String(validate=validate.Length(min=4, max=255))
    routing_number = fields.String(validate=validate.Length(min=9, max=9))
    bank_name = fields.String(required=True)
    account_type = fields.Enum(BankAccountType, required=True)
    
    # Plaid specific fields
    plaid_account_id = fields.String(dump_only=True)
    plaid_institution_id = fields.String(dump_only=True)
    account_mask = fields.String(dump_only=True)
    account_name = fields.String(dump_only=True)
    official_name = fields.String(dump_only=True)
    account_subtype = fields.String(dump_only=True)
    
    # Metadata fields
    is_active = fields.Boolean(dump_only=True)
    last_sync = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class BankAccountCreateSchema(BankAccountBaseSchema):
    pass

class BankAccountUpdateSchema(BankAccountBaseSchema):
    account_number = fields.String(validate=validate.Length(min=4, max=255))
    routing_number = fields.String(validate=validate.Length(min=9, max=9))
    bank_name = fields.String()
    account_type = fields.Enum(BankAccountType)

class PlaidLinkTokenSchema(Schema):
    link_token = fields.String(required=True)

class PlaidExchangeTokenSchema(Schema):
    public_token = fields.String(required=True)
    metadata = fields.Dict(required=True)

class BankTransactionSchema(Schema):
    id = fields.String(dump_only=True)
    account_id = fields.String(required=True)
    amount = fields.Float(required=True)
    date = fields.Date(required=True)
    description = fields.String(required=True)
    category = fields.List(fields.String())
    merchant_name = fields.String(allow_none=True)
    pending = fields.Boolean()

# Initialize schemas
bank_account_schema = BankAccountBaseSchema()
bank_accounts_schema = BankAccountBaseSchema(many=True)
bank_transaction_schema = BankTransactionSchema()
bank_transactions_schema = BankTransactionSchema(many=True)
