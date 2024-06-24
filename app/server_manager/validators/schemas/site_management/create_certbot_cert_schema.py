from marshmallow import Schema, fields, validates_schema, ValidationError, validate

from app.server_manager.validators.rules.domain_exist_rule import validate_domain_exist
from app.server_manager.validators.rules.domain_rule import validate_domain
from app.server_manager.validators.rules.nested_structure_rule import validate_nested_structure


class CreateCertBotCertificateSchema(Schema):
    domain = fields.Str(required=True, validate=[validate_domain, validate_domain_exist])
    email = fields.Email(required=True)
