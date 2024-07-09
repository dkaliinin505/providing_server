from marshmallow import Schema, fields


class CreateDatabaseUserSchema(Schema):
    db_user = fields.Str(validate=fields.Length(min=6, max=32))
    db_user_password = fields.Str(validate=fields.Length(min=6, max=32))
    db_privileges = fields.List(fields.Str(validate=fields.Length(min=6, max=32)), missing=['ALL PRIVILEGES'])
    db_host = fields.IPv4(required=True)
