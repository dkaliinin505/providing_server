import sys
import os

# add the app directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app_instance

if __name__ == "__main__":
    app_instance.run()
