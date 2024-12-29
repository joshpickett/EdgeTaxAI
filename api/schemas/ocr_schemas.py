from marshmallow import Schema, fields, validate
from .base_schemas import BaseSchema

class OCRLineItemSchema(Schema):
    description = fields.String()
    amount = fields.Decimal(places=2)
    quantity = fields.Integer(allow_none=True)
    unit_price = fields.Decimal(places=2, allow_none=True)

class OCRResultSchema(BaseSchema):
    document_id = fields.Integer(required=True)
    total_amount = fields.Decimal(places=2)
    date = fields.Date()
    vendor_name = fields.String()
    items = fields.List(fields.Nested(OCRLineItemSchema))
    confidence_score = fields.Float()
    raw_text = fields.String()
    metadata = fields.Dict(keys=fields.String(), values=fields.Raw())
    status = fields.String()
    error_message = fields.String(allow_none=True)

ocr_result_schema = OCRResultSchema()
ocr_results_schema = OCRResultSchema(many=True)
