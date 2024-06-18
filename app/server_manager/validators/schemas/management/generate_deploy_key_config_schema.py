from marshmallow import Schema, fields

from app.server_manager.validators.rules.domain_exist_rule import validate_domain_exist
from app.server_manager.validators.rules.domain_rule import validate_domain


class GenerateDeployKeyCommandSchema(Schema):
    domain = fields.Str(required=True, validate=[validate_domain, validate_domain_exist])
