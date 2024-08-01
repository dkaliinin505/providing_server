from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from app.server_manager.validators.rules.domain_rule import validate_domain
from app.server_manager.validators.rules.nested_structure_rule import validate_nested_structure


# In the future, we will add some webroot and other rows here
class DeleteSiteSchema(Schema):
    domain = fields.Str(required=True, validate=validate_domain)

    @validates_schema
    def validate_nested_structure_wrapper(self, data, **kwargs):
        validate_nested_structure(data)
