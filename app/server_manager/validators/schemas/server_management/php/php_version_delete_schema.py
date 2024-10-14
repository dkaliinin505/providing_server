from marshmallow import Schema, fields, validate, ValidationError
import subprocess

from app.server_manager.validators.rules.quantity_php_v import count_installed_php_versions


class PhpVersionDeleteSchema(Schema):
    php_version = fields.Str(required=True,
                             validate=[validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."), count_installed_php_versions])


