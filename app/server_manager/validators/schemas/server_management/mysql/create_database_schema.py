from marshmallow import Schema, fields, validates_schema, ValidationError


class CreateDatabaseSchema(Schema):
    db_name = fields.Str(required=True, validate=fields.Length(min=1, max=32))
    create_user = fields.Bool(missing=False)
    db_user = fields.Str(validate=fields.Length(min=6, max=32))
    db_user_password = fields.Str(validate=fields.Length(min=6, max=32))
    db_privileges = fields.List(fields.Str(validate=fields.Length(min=1, max=64)), missing=['ALL PRIVILEGES'])

    @validates_schema
    def validate_user_creation(self, data, **kwargs):
        if data.get('create_user'):
            if not data.get('db_user'):
                raise ValidationError('db_user is required when create_user is true', field_name='db_user')
            if not data.get('db_user_password'):
                raise ValidationError('db_user_password is required when create_user is true',
                                      field_name='db_user_password')
