from marshmallow import Schema, fields, validate
from datetime import datetime


class MileageSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    start_location = fields.Str(required=True, validate=validate.Length(max=255))
    end_location = fields.Str(required=True, validate=validate.Length(max=255))
    distance = fields.Float(required=True)
    date = fields.DateTime(required=True)
    purpose = fields.Str(validate=validate.Length(max=500))
    expense_id = fields.Int(allow_none=True)
    deduction_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class RecurringTripSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    start_location = fields.Str(required=True, validate=validate.Length(max=255))
    end_location = fields.Str(required=True, validate=validate.Length(max=255))
    frequency = fields.Str(
        required=True, validate=validate.OneOf(["daily", "weekly", "monthly"])
    )
    purpose = fields.Str(validate=validate.Length(max=500))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


mileage_schema = MileageSchema()
mileages_schema = MileageSchema(many=True)
recurring_trip_schema = RecurringTripSchema()
recurring_trips_schema = RecurringTripSchema(many=True)
