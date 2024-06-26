from marshmallow import Schema, fields, validates_schema, ValidationError, validate

from app.server_manager.validators.rules.domain_exist_rule import validate_domain_exist
from app.server_manager.validators.rules.domain_rule import validate_domain
from app.server_manager.validators.rules.nested_structure_rule import validate_nested_structure


class DeployProjectSchema(Schema):
    domain = fields.Str(required=True, validate=[validate_domain, validate_domain_exist])
    repository_url = fields.Str(required=True, validate=validate.Length(min=5, max=300))
    branch = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    is_nested_structure = fields.Bool(missing=False)
    nested_folder = fields.Str(validate=validate.Length(min=2, max=300))

    @validates_schema
    def validate_nested_structure_wrapper(self, data, **kwargs):
        validate_nested_structure(data)
