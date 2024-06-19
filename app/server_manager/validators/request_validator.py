import logging
from functools import wraps
from flask import request, jsonify
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
        и values are schema classes for validation.
    """
    key_validation_url = os.getenv('KEY_VALIDATION_URL')
    app_type = os.getenv('APP_TYPE', 'dev')

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            logger.debug("Entering decorator")

            if app_type != 'dev':
                # Check if the Authorization header is present
                authorization_header = request.headers.get('Authorization')
                if not authorization_header:
                    logger.debug("Authorization header is missing")
                    return jsonify({'errors': 'Authorization header is missing'}), 401

                # Key validation
                response = requests.get(key_validation_url, headers={'Authorization': authorization_header})
                if response.status_code != 200:
                    logger.debug("Invalid authorization token")
                    return jsonify({'errors': 'Invalid authorization token'}), 401

            method = request.method
            logger.debug(f"HTTP Method: {method}")
            logger.debug(f"Schema Class: {schema_classes}")

            if method in schema_classes:
                schema_class = schema_classes[method]
                validator = schema_class()
                logger.debug(f"Validator: {validator}")

                if method == 'DELETE' or method == 'GET':
                    data = request.args.to_dict()
                else:
                    data = request.get_json().get('config', {})

                logger.debug(f"Data: {data}")

                if isinstance(validator, InstallPackageSchema):
                    package_name = data.get('package_name')

                    try:
                        config_validator = validator.load_config(package_name)
                    except ValidationError as e:
                        logger.debug(f"Validation error: {e.messages}")
                        return jsonify({'errors': e.messages}), 400

                    config_errors = config_validator.validate(data.get('config', {}))
                    if config_errors:
                        logger.debug(f"Config validation errors: {config_errors}")
                        return jsonify({'errors': config_errors}), 400
                else:
                    errors = validator.validate(data)
                    if errors:
                        logger.debug(f"Validation errors: {errors}")
                        return jsonify({'errors': errors}), 400

                kwargs['data'] = data
                logger.debug(f"kwargs['data']: {kwargs['data']}")
            return f(*args, **kwargs)

        return decorated_function

    return decorator
