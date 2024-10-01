from marshmallow import Schema, fields


class RestartQueueWorkerSchema(Schema):
    worker_id = fields.Raw(required=True)