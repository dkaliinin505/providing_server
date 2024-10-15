from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from app.server_manager.validators.schemas.server_management.scheduler.custom_scheuler_schema import CustomScheduleSchema


class CreateSchedulerJobSchema(Schema):
    user = fields.Str(required=True, validate=validate.Length(min=1))
    command = fields.Str(required=True, validate=validate.Length(min=1))
    frequency = fields.Str(required=True, validate=validate.OneOf(
        ['Every Minute', 'Hourly', 'Nightly', 'Weekly', 'Monthly', 'On Reboot', 'custom']))
    custom_schedule = fields.Nested(CustomScheduleSchema, required=False)  # Only required if frequency is 'custom'

    @validates_schema
    def validate_custom_schedule(self, data, **kwargs):
        if data['frequency'] == 'custom' and 'custom_schedule' not in data:
            raise ValidationError("custom_schedule is required when frequency is 'custom'.")
        if data['frequency'] != 'custom' and 'custom_schedule' in data:
            raise ValidationError("custom_schedule should only be provided when frequency is 'custom'.")
