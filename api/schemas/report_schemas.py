from marshmallow import Schema, fields, validate
from datetime import datetime


class ReportBaseSchema(Schema):
    user_id = fields.Int(required=True)
    year = fields.Int(required=False, default=lambda: datetime.now().year)
    format = fields.Str(
        validate=validate.OneOf(["json", "pdf", "excel"]), default="json"
    )


class TaxSummarySchema(ReportBaseSchema):
    categories = fields.List(fields.Str(), required=False)
    include_predictions = fields.Bool(default=False)


class ExpenseReportSchema(ReportBaseSchema):
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    categories = fields.List(fields.Str(), required=False)


class AnalyticsReportSchema(ReportBaseSchema):
    analysis_type = fields.List(fields.Str(), required=False)
    include_predictions = fields.Bool(default=False)
