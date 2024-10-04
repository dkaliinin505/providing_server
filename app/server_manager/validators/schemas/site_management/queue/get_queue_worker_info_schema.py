from marshmallow import Schema, fields


class GetQueueWorkerInfoSchema(Schema):
    worker_id = fields.Raw(required=True)
