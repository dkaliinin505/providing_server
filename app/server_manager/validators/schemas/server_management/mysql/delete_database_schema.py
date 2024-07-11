from marshmallow import Schema, fields, validate


class DeleteDatabaseSchema(Schema):
    db_name = fields.Str(required=True, validate=validate.Length(min=1, max=32))
