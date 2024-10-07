from marshmallow import Schema, fields, validate, ValidationError, validates_schema


class PullProjectSchema(Schema):
    php = fields.Str(required=True, validate=validate.Regexp(r'^php[0-9.]*$', error="Invalid PHP version format"))
    php_fpm = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    composer = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    site_branch = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    user_script = fields.Str(required=True)

    @validates_schema
    def validate_script(self, data, **kwargs):
        if 'git pull' not in data.get('user_script', ''):
            raise ValidationError('user_script must contain a git pull command.')
        if 'composer install' not in data.get('user_script', ''):
            raise ValidationError('user_script must contain a composer install command.')
