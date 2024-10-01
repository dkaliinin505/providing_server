from marshmallow import Schema, fields


class GetQueueWorkerLogsSchema(Schema):
    worker_id = fields.Raw(required=True)