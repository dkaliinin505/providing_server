from marshmallow import Schema, fields, validate, ValidationError


class DeleteScheduledJobSchema(Schema):
    user = fields.Str(required=True, validate=validate.Length(min=1))
    job_id = fields.Str(required=True, validate=validate.Length(min=1))
