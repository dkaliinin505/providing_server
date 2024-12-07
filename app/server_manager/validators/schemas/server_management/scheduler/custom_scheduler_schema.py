from marshmallow import Schema, fields, ValidationError, validates


class IntOrStar(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if value == '*':
            return value
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError("Value must be int or '*'.")

        return int_value


class CustomScheduleSchema(Schema):
    minute = IntOrStar(required=True)
    hour = IntOrStar(required=True)
    day_of_week = IntOrStar(required=True)
    day_of_month = IntOrStar(required=True)
    month = IntOrStar(required=True)

    @validates('minute')
    def validate_minute(self, value):
        if value == '*':
            return
        if not (0 <= value <= 59):
            raise ValidationError("Field 'minute' must be from 0 to 59.")

    @validates('hour')
    def validate_hour(self, value):
        if value == '*':
            return
        if not (0 <= value <= 23):
            raise ValidationError("Field 'hour' must be from  0 to 23.")

    @validates('day_of_week')
    def validate_day_of_week(self, value):
        if value == '*':
            return
        if not (0 <= value <= 6):
            raise ValidationError("Field 'day_of_week' must be from 0 to 6.")

    @validates('day_of_month')
    def validate_day_of_month(self, value):
        if value == '*':
            return
        if not (1 <= value <= 31):
            raise ValidationError("Field 'day_of_month' must be from 1 to 31.")

    @validates('month')
    def validate_month(self, value):
        if value == '*':
            return
        if not (1 <= value <= 12):
            raise ValidationError("Field 'month' must be from 1 to 12.")
