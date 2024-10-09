import asyncio
import logging
import aiohttp
import aiofiles
import re
from aiofiles import os

from utils.env_util import async_get_env_variable


async def run_command_async(command, raise_exception=True, capture_output=False):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout_decoded = stdout.decode()
    stderr_decoded = stderr.decode()

    if process.returncode != 0:
        error_message = f"Command '{command}' failed with error: {stderr_decoded}"
        if raise_exception:
            raise Exception(error_message)
        if capture_output:
            return stdout_decoded, stderr_decoded
        return None

    if capture_output:
        return stdout_decoded, stderr_decoded
    return stdout_decoded


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


async def extract_error_message(error_message: str):
    match = re.search(r"failed with error:(.*)", error_message)
    if match:
        return match.group(1).strip()
    return error_message


async def remove_ansi_escape_codes(text: str):
    ansi_escape_pattern = re.compile(
        r'(?:\x1B[@-Z\\-_]|\x1B\[[0-?]*[ -/]*[@-~])'  # ESC sequences
        r'|\x1B\[[0-9;]*[A-Za-z]'  # CSI sequences
        r'|\x1B\(.[a-zA-Z]'  # OS Command sequences
        r'|\x1B\]8;;[^ ]+ '  # Hyperlinks
        r'|\x1B]2;.*?\x07',  # Window title sequences
        flags=re.VERBOSE
    )
    return ansi_escape_pattern.sub('', text)
