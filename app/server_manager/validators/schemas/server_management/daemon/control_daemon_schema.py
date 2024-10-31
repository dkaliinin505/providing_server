from marshmallow import Schema, fields, validate, ValidationError


class ControlDaemonSchema(Schema):
    daemon_id = fields.Str(required=True),
    num_processes = fields.Int(required=True, validate=validate.Range(min=1, max=100))
    action = fields.Str(required=True, validate=validate.OneOf(['start', 'stop', 'restart']))