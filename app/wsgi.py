import sys
import os
from flask import jsonify

# Add the app directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app_instance
from app.exceptions.http_exception import ProvidingServerHTTPException


@app_instance.app.errorhandler(Exception)
def handle_exception(e):
    # If the exception is a custom one, use its status code and message
    if isinstance(e, ProvidingServerHTTPException):
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response

    # Handle non-HTTP exceptions
    response = jsonify({
        "code": 500,
        "name": "Internal Server Error",
        "description": str(e)
    })
    response.status_code = 500
    return response


if __name__ == "__main__":
    app_instance.run()
