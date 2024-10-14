from marshmallow import Schema, fields, validate, ValidationError


class PhpGetConfigFileSchema(Schema):
    php_type = fields.Str(required=True, validate=validate.OneOf(['cli', 'fpm']))
    php_version = fields.Str(required=True,
                             validate=validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."))
