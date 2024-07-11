import os
from dotenv import load_dotenv, set_key, dotenv_values
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()


def load_env(env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_file_path)


def update_env_variable(key, value, env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    set_key(env_file_path, key, value, "never")
    # Reload the environment variables after updating
    load_env(env_file_path)


def get_env_variable(key, env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    env_vars = dotenv_values(env_file_path)
    return env_vars.get(key)


async def async_load_env(env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    await asyncio.get_event_loop().run_in_executor(executor, load_dotenv, env_file_path)


async def async_update_env_variable(key, value, env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    await asyncio.get_event_loop().run_in_executor(executor, set_key, env_file_path, key, value, "never")
    # Reload the environment variables after updating
    await async_load_env(env_file_path)


async def async_get_env_variable(key, env_file_path=None):
    if env_file_path is None:
        env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    env_vars = await asyncio.get_event_loop().run_in_executor(executor, dotenv_values, env_file_path)
    return env_vars.get(key)
