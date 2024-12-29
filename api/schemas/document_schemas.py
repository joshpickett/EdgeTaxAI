from marshmallow import Schema, fields, validate
from .base_schemas import AuditSchema
from api.models.documents import DocumentType, DocumentStatus

class DocumentVersionSchema(Schema):
    id = fields.Integer(dump_only=True)
    version_number = fields.Integer(required=True)
    file_path = fields.String(required=True)
    changes = fields.Dict(keys=fields.String(), values=fields.Raw())
    created_by = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class DocumentSchema(AuditSchema):
    type = fields.Enum(DocumentType, required=True)
    filename = fields.String(required=True, validate=validate.Length(max=255))
    file_path = fields.String(required=True, validate=validate.Length(max=512))
    mime_type = fields.String(validate=validate.Length(max=100))
    size = fields.Integer()
    status = fields.Enum(DocumentStatus, dump_default=DocumentStatus.PENDING)
    metadata = fields.Dict(keys=fields.String(), values=fields.Raw())
    current_version = fields.Nested(DocumentVersionSchema, dump_only=True)
    versions = fields.List(fields.Nested(DocumentVersionSchema), dump_only=True)

document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)
