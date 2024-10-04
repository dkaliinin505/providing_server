from marshmallow import Schema, fields, validates_schema, ValidationError, validate, validates


class CreateQueueWorkerSchema(Schema):
    worker_id = fields.Raw(required=True)
    artisan_path = fields.Str(required=True)
    connection = fields.Str(required=True, validate=validate.OneOf(["database", "redis"]))
    queue = fields.Str(required=True)
    sleep = fields.Int(required=True, validate=validate.Range(min=10))
    timeout = fields.Int(required=True, validate=validate.Range(min=60))
    delay = fields.Int(required=True, validate=validate.Range(min=10))
    memory = fields.Int(required=True, validate=validate.Range(min=128))
    tries = fields.Int(required=True, validate=validate.Range(min=1))

    @validates('worker_id')
    def validate_worker_id(self, value):
        if not isinstance(value, (str, int)):
            raise ValidationError("worker_id must be either a string or an integer.")

    @validates('artisan_path')
    def validate_artisan_path(self, value):
        if not value.endswith('artisan'):
            raise ValidationError("The path must point to the 'artisan' file.")

    @validates('queue')
    def validate_queue(self, value):
        queue_names = value.split(",")
        for queue_name in queue_names:
            if not queue_name.strip():
                raise ValidationError(f"Queue name '{queue_name}' is not valid.")

        for queue_name in queue_names:
            if not queue_name.strip().isalnum():
                raise ValidationError(f"Queue name '{queue_name}' should contain only alphanumeric characters.")
