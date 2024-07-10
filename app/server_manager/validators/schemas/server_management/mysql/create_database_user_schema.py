from marshmallow import Schema, fields, validate


class CreateDatabaseUserSchema(Schema):
    db_user = fields.Str(validate=fields.Length(min=6, max=32))
    db_user_password = fields.Str(validate=fields.Length(min=6, max=32))
    db_privileges = fields.List(fields.Str(validate=fields.Length(min=3, max=64)), missing=['ALL PRIVILEGES'])
    db_name = fields.List(fields.Str(validate=validate.Length(min=1, max=64)), required=False)
