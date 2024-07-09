from marshmallow import Schema, fields


class CreateDatabaseUserSchema(Schema):
    db_user = fields.Str()
    db_user_password = fields.Str()
    db_privileges = fields.List(fields.Str(), missing=['SELECT'])
