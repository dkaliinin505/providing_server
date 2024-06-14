from marshmallow import Schema, fields


class MysqlConfigSchema(Schema):
    db_password = fields.Str(required=True, validate=fields.Length(min=8, max=32))
    initial_db = fields.Str(required=True, validate=fields.Length(min=8, max=32))
    remote_ip = fields.IPv4(required=True)
