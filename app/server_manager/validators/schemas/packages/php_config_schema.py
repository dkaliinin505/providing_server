from marshmallow import Schema, fields


class PhpConfigSchema(Schema):
    memory_limit = fields.Str(required=True)
    request_terminate_timeout = fields.Int(required=False)
    pm_max_children = fields.Int(required=False)
