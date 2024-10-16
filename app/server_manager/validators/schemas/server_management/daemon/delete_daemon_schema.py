from marshmallow import Schema, fields, validate, ValidationError


class DeleteDaemonSchema(Schema):
    daemon_id = fields.Str(required=True)
