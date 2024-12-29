from marshmallow import Schema, fields, validate
from .base_schemas import BaseSchema
import enum

class BatchStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class BatchItemSchema(Schema):
    filename = fields.String(required=True)
    status = fields.String()
    error_message = fields.String(allow_none=True)
    processing_time = fields.Float(dump_only=True)
    result = fields.Dict(keys=fields.String(), values=fields.Raw())

class BatchProcessingSchema(BaseSchema):
    batch_id = fields.String(dump_only=True)
    user_id = fields.Integer(required=True)
    status = fields.Enum(BatchStatus, dump_default=BatchStatus.PENDING)
    total_items = fields.Integer(dump_only=True)
    processed_items = fields.Integer(dump_only=True)
    failed_items = fields.Integer(dump_only=True)
    start_time = fields.DateTime(dump_only=True)
    completion_time = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(BatchItemSchema))

batch_processing_schema = BatchProcessingSchema()
batch_processings_schema = BatchProcessingSchema(many=True)
