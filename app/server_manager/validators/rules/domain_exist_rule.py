import socket

from marshmallow import ValidationError


def validate_domain_existence(domain):
    try:
        socket.gethostbyname(domain)
    except socket.error:
        raise ValidationError(f"Domain '{domain}' does not exist.")
