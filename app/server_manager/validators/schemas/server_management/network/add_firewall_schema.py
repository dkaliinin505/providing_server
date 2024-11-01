from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from app.server_manager.validators.schemas.server_management.scheduler.custom_scheuler_schema import CustomScheduleSchema


class AddFirewallRuleSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    port = fields.Int(required=True, validate=validate.Range(min=1, max=65535))
    from_ip = fields.Str(required=False, allow_none=True)   # Optional
    rule_id = fields.Str(required=True, validate=validate.Length(min=1))
    rule_type = fields.Str(required=False, validate=validate.OneOf(['allow', 'deny']), missing='allow')  # Optional, default 'allow'