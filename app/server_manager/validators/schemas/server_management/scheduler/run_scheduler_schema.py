from marshmallow import Schema, fields, validate


class RunSchedulerJobSchema(Schema):
    command = fields.Str(required=True, validate=validate.Length(min=1))
