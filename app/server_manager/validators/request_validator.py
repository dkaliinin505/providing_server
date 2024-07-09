import logging
from functools import wraps
from quart import request, jsonify, make_response
from marshmallow import ValidationError
import os
import requests

from app.server_manager.validators.schemas.install_package_schema import InstallPackageSchema

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def validate_request(schema_classes):
    """
    schema_classes: dict
        A dictionary where keys are HTTP methods (GET, POST, etc.)
        and values are schema classes for validation.
    """
    key_validation_url = os.getenv('KEY_VALIDATION_URL')
    app_type = os.getenv('APP_TYPE', 'dev')

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            logger.debug("Entering decorator")

            if app_type != 'dev':
                # Check if the Authorization header is present
                authorization_header = request.headers.get('Authorization')
                if not authorization_header:
                    logger.debug("Authorization header is missing")
                    response = jsonify({'errors': 'Authorization header is missing'})
                    response.status_code = 401
                    return response

                # Key validation
                response = requests.get(key_validation_url, headers={'Authorization': authorization_header})
                if response.status_code != 200:
                    logger.debug("Invalid authorization token")
                    response = jsonify({'errors': 'Invalid authorization token'})
                    response.status_code = 401
                    return response

            method = request.method
            logger.debug(f"HTTP Method: {method}")
            logger.debug(f"Schema Class: {schema_classes}")

            if method in schema_classes:
                schema_class = schema_classes[method]
                validator = schema_class()
                logger.debug(f"Validator: {validator}")

                data = await get_request_data(method)

                logger.debug(f"Data: {data}")

                errors = validate_data(validator, data)
                if errors:
                    logger.debug(f"Validation errors: {errors}")
                    response = jsonify({'errors': errors})
                    response.status_code = 400
                    return response

                if isinstance(validator, InstallPackageSchema):
                    package_name = data.get('package_name')
                    config_validator = get_config_validator(validator, package_name)
                    if not config_validator:
                        response = jsonify({'errors': 'Invalid package name'})
                        response.status_code = 400
                        return response

                    config_errors = config_validator.validate(data.get('config', {}))
                    if config_errors:
                        logger.debug(f"Config validation errors: {config_errors}")
                        response = jsonify({'errors': config_errors})
                        response.status_code = 400
                        return response

                kwargs['data'] = data
                logger.debug(f"kwargs['data']: {kwargs['data']}")

            return await f(*args, **kwargs)

        return decorated_function

    return decorator


async def get_request_data(method):
    if method in ['DELETE', 'GET']:
        logger.debug("GET or DELETE request")
        return request.args.to_dict()
    else:
        return await request.get_json()


def validate_data(validator, data):
    errors = validator.validate(data)
    if errors:
        logger.debug(f"Validation errors: {errors}")
    return errors


def get_config_validator(validator, package_name):
    try:
        return validator.load_config(package_name)
    except ValidationError as e:
        logger.debug(f"Validation error: {e.messages}")
        return None
