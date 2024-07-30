from marshmallow import Schema, fields


class MysqlConfigSchema(Schema):
    initial_db = fields.Str(required=True, validate=fields.Length(min=1, max=32))
