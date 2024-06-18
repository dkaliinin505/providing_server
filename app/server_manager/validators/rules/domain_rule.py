import re
from marshmallow import ValidationError

DOMAIN_REGEX = re.compile(
    r'^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.([A-Za-z]{2,6}|[A-Za-z0-9-]{2,30}\.[A-Za-z]{2,3})$'
)


def validate_domain(value):
    if not DOMAIN_REGEX.match(value):
        raise ValidationError("Invalid domain name.")
