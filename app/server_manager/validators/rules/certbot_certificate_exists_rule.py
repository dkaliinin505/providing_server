from marshmallow import ValidationError

from utils.util import run_command


def validate_certbot_certificate_exists(domain):
    try:
        # Check if the certificate exists for the given domain
        result = run_command(f"certbot certificates -d {domain}", return_json=False, raise_exception=False)

        # Check if the output contains the domain
        if domain not in result:
            raise ValidationError(f"Certificate for domain {domain} does not exist.")
    except Exception as e:
        raise ValidationError(f"Error checking certificate for domain {domain}: {str(e)}")
