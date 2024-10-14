from marshmallow import Schema, fields, validate, ValidationError


class PhpVersionInstallSchema(Schema):
    php_version = fields.Str(required=True,
                             validate=validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."))
