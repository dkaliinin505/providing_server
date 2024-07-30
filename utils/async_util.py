import asyncio
import logging
import aiohttp
import aiofiles
from aiofiles import os

from utils.env_util import async_get_env_variable


async def run_command_async(command, raise_exception=True):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        if raise_exception:
            raise Exception(f"Command '{command}' failed with error: {stderr.decode()}")
        return None
    return stdout.decode()


async def check_file_exists(filepath):
    try:
        async with aiofiles.open(filepath, 'r'):
            return True
    except FileNotFoundError:
        return False


async def dir_exists(dirpath):
    try:
        if await aiofiles.os.path.isdir(dirpath):
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking if directory exists: {e}")
        return False


async def send_post_request_async(data):
    url = await async_get_env_variable("CALLBACK_URL")
    if not url:
        raise Exception("CALLBACK_URL not set in .env file")

    logging.info(f"Sending POST request to {url} with data: {data}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data) as response:
                response.raise_for_status()
                logging.info(f"Request successful, response: {await response.json()}")
                return await response.json()
        except aiohttp.ClientError as e:
            logging.error(f"Request failed: {e}")
            return None