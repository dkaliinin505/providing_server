from marshmallow import Schema, fields


class CreateDatabaseSchema(Schema):
    db_name = fields.Str(required=True, validate=fields.Length(min=1, max=32))
    create_user = fields.Bool(missing=False)
    db_user = fields.Str(validate=fields.Length(min=6, max=32))
    db_user_password = fields.Str(validate=fields.Length(min=6, max=32))
    db_privileges = fields.List(fields.Str(validate=fields.Length(min=6, max=64)), missing=['ALL PRIVILEGES'])
