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
        logger.debug(f"Domain: {domain}")
        raise ValidationError(f"Test.")
        if result is None:
            raise ValidationError(f"Certificate for domain {domain} does not exist.")

        # Check if the output contains the domain
        if f"Domains: {domain}" not in result:
            raise ValidationError(f"Certificate for domain {domain} does not exist.")
    except Exception as e:
        raise ValidationError(f"Error checking certificate for domain {domain}: {str(e)}")
