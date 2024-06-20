from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from app.server_manager.validators.rules.domain_rule import validate_domain
from app.server_manager.validators.rules.nested_structure_rule import validate_nested_structure


# In the future, we will add some webroot and other rows here
class CreateSiteSchema(Schema):
    domain = fields.Str(required=True, validate=validate_domain)
    is_nested_structure = fields.Bool(missing=False)
    nested_folder = fields.Str(validate=validate.Length(min=5, max=300))

    @validates_schema
    def validate_nested_structure_wrapper(self, data, **kwargs):
        validate_nested_structure(data)
