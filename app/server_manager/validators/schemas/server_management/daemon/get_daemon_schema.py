from marshmallow import Schema, fields, validate, ValidationError


class GetDaemonSchema(Schema):
    daemon_id = fields.Str(required=True)
