# self.user = self.config.get('user')
#         self.ssh_key = self.config.get('ssh_key')
from marshmallow import Schema, fields, validate, ValidationError, validates_schema, validates
import pwd
from app.server_manager.validators.rules.domain_rule import validate_domain
from app.server_manager.validators.rules.nested_structure_rule import validate_nested_structure


class AddSSHKeySchema(Schema):
    key_id = fields.Str(required=True, validate=validate.Length(min=1))
    user = fields.Str(required=True)
    ssh_key = fields.Str(required=True)

    @validates_schema
    def validate_user(self, data, **kwargs):
        try:
            pwd.getpwnam(data.get('user'))
        except KeyError:
            raise ValidationError(f"User '{data.get('user')}' does not exist.")
