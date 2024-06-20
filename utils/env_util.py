import os
from dotenv import load_dotenv, set_key, dotenv_values


def load_env(env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_file_path)


def update_env_variable(key, value, env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    set_key(env_file_path, key, value)
    # Reload the environment variables after updating
    load_env(env_file_path)


def get_env_variable(key, env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = dotenv_values(env_file_path)
    return env_vars.get(key)
