# self.user = self.config.get('user')
#         self.ssh_key = self.config.get('ssh_key')
from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from app.server_manager.validators.rules.domain_rule import validate_domain
from app.server_manager.validators.rules.nested_structure_rule import validate_nested_structure


class AddSSHKeySchema(Schema):
    user = fields.Str(required=True)
    ssh_key = fields.Str(required=True)
