from marshmallow import Schema, fields, validate

class BaseSchema(Schema):
    """Base schema with common fields for all models"""
    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class AuditSchema(BaseSchema):
    """Schema for models that require audit tracking"""
    created_by = fields.Integer(dump_only=True)
    updated_by = fields.Integer(dump_only=True)
    version = fields.Integer(dump_only=True, default=1)
    
    class Meta:
        """Schema metadata"""
        ordered = True
        strict = True
        dateformat = '%Y-%m-%dT%H:%M:%S'
