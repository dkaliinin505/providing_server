import requests
from functools import wraps
from flask import request, jsonify
import os


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

            # Validation of data
            method = request.method
            if method in schema_classes:
                schema_class = schema_classes[method]
                validator = schema_class()
                data = request.get_json()
                errors = validator.validate(data)
                if errors:
                    return jsonify({'errors': errors}), 400
                kwargs['data'] = data
            return f(*args, **kwargs)

        return decorated_function

    return decorator
