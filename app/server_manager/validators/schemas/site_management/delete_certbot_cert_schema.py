from marshmallow import fields, Schema

from app.server_manager.validators.rules.domain_exist_rule import validate_domain_exist
from app.server_manager.validators.rules.domain_rule import validate_domain


class DeleteCertBotCertificateSchema(Schema):
    domain = fields.Str(required=True, validate=[validate_domain, validate_domain_exist])