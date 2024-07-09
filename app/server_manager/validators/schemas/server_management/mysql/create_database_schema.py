from marshmallow import Schema, fields


class CreateDatabaseSchema(Schema):
    db_name = fields.Str(required=True)
    create_user = fields.Bool(missing=False)
    db_user = fields.Str()
    db_user_password = fields.Str()
    db_host = fields.Str(missing='%')
