from marshmallow import Schema, fields, validate, ValidationError


class PhpToggleOpcacheSchema(Schema):
    php_version = fields.Str(required=True,
                             validate=validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."))
    enable_opcache = fields.Bool(required=True, validate=validate.OneOf([True, False]))
