from marshmallow import Schema, fields


class RequestSchema(Schema):
    param1 = fields.Str(required=False)
    param2 = fields.Str(required=False)


class AnotherRequestSchema(Schema):
    param3 = fields.Str(required=True)
    param4 = fields.Str(required=True)
