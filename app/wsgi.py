import sys
import os

# Add the app directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app_instance
from utils.env_util import load_env


# Load environment variables before the first request
@app_instance.before_first_request
def reload_env_vars():
    load_env()


if __name__ == "__main__":
    load_env()  # Load environment variables before running the app
    app_instance.run()
