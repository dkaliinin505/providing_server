from marshmallow import Schema, fields


class MysqlConfigSchema(Schema):
    db_password = fields.Str(required=True)
    initial_db = fields.Str(required=True)
    remote_ip = fields.IPv4(required=True)
