from marshmallow import Schema, fields, validate


class DeleteDatabaseUserSchema(Schema):
    db_user = fields.Str(required=True, validate=validate.Length(min=1, max=32))
