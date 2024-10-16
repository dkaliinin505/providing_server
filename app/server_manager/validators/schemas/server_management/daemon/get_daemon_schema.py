from marshmallow import Schema, fields, validate, ValidationError


class GetDaemonSchema(Schema):
    user = fields.Str(missing='super_forge', validate=validate.Length(min=1))
    daemon_id = fields.Str(required=True)
