import os

from marshmallow import Schema, fields, validate, ValidationError, validates_schema

from app.server_manager.validators.rules.domain_rule import validate_domain
from app.server_manager.validators.rules.nested_structure_rule import validate_nested_structure


# In the future, we will add some webroot and other rows here
class ServerLogsSchema(Schema):
    log_path = fields.Str(required=True)

    @validates_schema
    def validate_if_logs_path_exist(self, data, **kwargs):
        if not os.path.exists(data.get('log_path')):
            raise ValidationError(f"Log file at {data.get('log_path')} not found.")
