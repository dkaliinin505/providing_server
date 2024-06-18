import os

from marshmallow import ValidationError


def validate_domain_exist(domain):
    nginx_conf_path = f"/etc/nginx/sites-available/{domain}"
    if not os.path.isfile(nginx_conf_path):
        raise ValidationError(f"Configuration file for domain '{domain}' does not exist.")
