import sys
import os
from app import app_instance


# add the app directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


if __name__ == "__main__":
    app_instance.run()
