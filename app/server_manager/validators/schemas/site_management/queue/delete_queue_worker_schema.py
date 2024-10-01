from marshmallow import Schema, fields, validates_schema, ValidationError, validate, validates


class DeleteQueueWorkerSchema(Schema):
    worker_id = fields.Raw(required=True)