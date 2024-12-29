from marshmallow import Schema, fields, validate
from .base_schemas import AuditSchema
from api.models.tax_forms import FormStatus, FormType
from .document_schemas import DocumentSchema

class TaxFormSchema(AuditSchema):
    form_type = fields.Enum(FormType, required=True)
    document_id = fields.Integer(allow_none=True)
    is_amended = fields.Boolean(default=False)
    notes = fields.String(validate=validate.Length(max=1000))
    document = fields.Nested(DocumentSchema, dump_only=True)

    ...rest of the code...
