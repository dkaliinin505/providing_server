from marshmallow import Schema, fields, validate, ValidationError


class PhpVersionInstallSchema(Schema):
    php_version = fields.Str(required=True,
                             validate=validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."))
    cli_default_version = fields.Str(missing='8.1',
                                     validate=validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."))
    sites_default_version = fields.Str(missing='8.1',
                                       validate=validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."))
