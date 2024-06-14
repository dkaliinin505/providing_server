from marshmallow import Schema, fields, validate

from app.server_manager.validators.rules.memory_limit_rule import validate_memory_limit


class PhpConfigSchema(Schema):
    memory_limit = fields.Str(required=True, validate=validate_memory_limit)
    request_terminate_timeout = fields.Int(required=False, validate=validate.Range(min=60, max=300))
    pm_max_children = fields.Int(required=False, validate=validate.Range(min=10, max=30))
