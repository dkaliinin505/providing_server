import logging

from marshmallow import ValidationError

from utils.util import run_command

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def validate_certbot_certificate_exists(domain):
    try:
        # Check if the certificate exists for the given domain
        result = run_command(f"sudo certbot certificates -d {domain}", return_json=False, raise_exception=False)
        logger.debug(f"Result: {result}")

        # Split the result into lines
        result_lines = result.splitlines()

        # Iterate through the lines to find the line containing the domain
        domain_exists = False
        for line in result_lines:
            if f"Domains: {domain}" in line:
                domain_exists = True
                break

        if not domain_exists:
            raise ValidationError(f"Certificate for domain {domain} does not exist.")
    except Exception as e:
        raise ValidationError(f"Error checking certificate for domain {domain}: {str(e)}")
