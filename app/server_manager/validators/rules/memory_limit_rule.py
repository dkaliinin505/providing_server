from marshmallow import ValidationError
import re


def validate_memory_limit(value):
    # Check if the value is in the correct format
    if not re.match(r'^\d+M$', value):
        raise ValidationError("Invalid format for memory_limit. It should be a number followed by 'M'. Example: '512M'")

    # Take the numeric value
    num_value = int(value[:-1])
    if num_value > 1024:
        raise ValidationError("memory_limit cannot exceed 1024M.")
