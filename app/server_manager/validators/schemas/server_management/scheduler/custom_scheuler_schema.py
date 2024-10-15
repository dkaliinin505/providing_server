from marshmallow import Schema, fields, validate


class CustomScheduleSchema(Schema):
    minute = fields.Int(required=True, validate=validate.Range(min=0, max=59))
    hour = fields.Int(required=True, validate=validate.Range(min=0, max=23))
    day_of_week = fields.Int(required=True, validate=validate.Range(min=0, max=6))
    day_of_month = fields.Int(required=True, validate=validate.Range(min=1, max=31))
    month = fields.Int(required=True, validate=validate.Range(min=1, max=12))
