from marshmallow import Schema, fields, validates_schema, ValidationError, validate

from app.server_manager.validators.rules.domain_exist_rule import validate_domain_exist
from app.server_manager.validators.rules.domain_rule import validate_domain


class DeploySiteSchema(Schema):
    domain = fields.Str(required=True, validate=[validate_domain, validate_domain_exist])
    repository_url = fields.Url(required=True)
    branch = fields.Str(required=True, validate=validate.Range(min=5, max=300))
    nested_structure = fields.Bool(missing=False)
    nested_folder = fields.Str(validate=validate.Range(min=5, max=300))

    @validates_schema
    def validate_nested_structure(self, data, **kwargs):
        if data.get('nested_structure'):
            if not data.get('nested_folder'):
                raise ValidationError('nested_folder must be provided if nested_structure is True')
        else:
            data.pop('nested_folder', None)
