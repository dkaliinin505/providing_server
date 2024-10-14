from marshmallow import Schema, fields, validate, ValidationError


class PhpConfigUpdateSchema(Schema):
    php_version = fields.Str(required=True,
                             validate=validate.Regexp(r'^\d+\.\d+$', error="Invalid PHP version format."))
    config_updates = fields.Dict(
        keys=fields.Str(validate=validate.OneOf([
            'upload_max_filesize',
            'max_execution_time',
            'memory_limit',
            'post_max_size'
        ])),
        values=fields.Str(),
        required=True
    )
