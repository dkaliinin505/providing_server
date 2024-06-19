from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError
import os
import requests

from app.server_manager.validators.schemas.install_package_schema import InstallPackageSchema


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
        def decorated_function(*args, **kwargs):

            if app_type != 'dev':
                # Check if the Authorization header is present
                authorization_header = request.headers.get('Authorization')
                if not authorization_header:
                    return jsonify({'errors': 'Authorization header is missing'}), 401

                # Key validation
                response = requests.get(key_validation_url, headers={'Authorization': authorization_header})
                if response.status_code != 200:
                    return jsonify({'errors': 'Invalid authorization token'}), 401

            method = request.method
            if method in schema_classes:
                schema_class = schema_classes[method]
                validator = schema_class()

                if method == 'DELETE' or method == 'GET':
                    data = request.args.to_dict()
                else:
                    data = request.get_json()

                if isinstance(validator, InstallPackageSchema):
                    package_name = data.get('package_name')

                    try:
                        config_validator = validator.load_config(package_name)
                    except ValidationError as e:
                        return jsonify({'errors': e.messages}), 400

                    config_errors = config_validator.validate(data.get('config', {}))
                    if config_errors:
                        return jsonify({'errors': config_errors}), 400
                else:
                    errors = validator.validate(data)
                    if errors:
                        return jsonify({'errors': errors}), 400

                kwargs['data'] = data
                print(f"Data: {data}")
            return f(*args, **kwargs)

        return decorated_function

    return decorator
