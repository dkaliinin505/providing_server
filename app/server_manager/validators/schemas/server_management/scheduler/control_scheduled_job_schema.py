from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from app.server_manager.validators.schemas.server_management.scheduler.custom_scheduler_schema import \
    CustomScheduleSchema


class ControlScheduledJobSchema(Schema):
    user = fields.Str(required=True, validate=validate.Length(min=1))
    job_id = fields.Str(required=True, validate=validate.Length(min=1))
    action = fields.Str(required=True, validate=validate.OneOf(['start', 'stop']))
