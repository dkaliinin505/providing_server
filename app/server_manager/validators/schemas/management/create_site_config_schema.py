from marshmallow import Schema, fields

from app.server_manager.validators.rules.domain_rule import validate_domain


# In the future, we will add some webroot and other rows here
class CreateSiteConfigSchema(Schema):
    domain = fields.Str(required=True, validate=validate_domain)
