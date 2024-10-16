from marshmallow import Schema, fields, validate, ValidationError


class ControlDaemonSchema(Schema):
    daemon_id = fields.Str(required=True)
    action = fields.Str(required=True, validate=validate.OneOf(['start', 'stop', 'restart']))