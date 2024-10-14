from marshmallow import Schema, fields, validate, ValidationError


class PhpUpdateConfigFileSchema(Schema):
    php_version = fields.Str(required=True,
                             validate=validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."))
    type = fields.Str(required=True, validate=validate.OneOf(['cli', 'fpm']))
    content = fields.Str(required=True)
