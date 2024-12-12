import asyncio
import codecs
import logging
import aiohttp
import aiofiles
import re
from aiofiles import os

from utils.env_util import async_get_env_variable

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def run_command_async(command, raise_exception=True, capture_output=False):
    logger.debug(f"Executing command: {command}")

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    stdout_decoded = stdout.decode()
    stderr_decoded = stderr.decode()

    logger.debug(f"Command stdout: {stdout_decoded}")
    logger.debug(f"Command stderr: {stderr_decoded}")
    logger.debug(f"Command exit code: {process.returncode}")

    if process.returncode != 0:
        error_message = f"Command '{command}' failed with error: {stderr_decoded}"
        logger.error(error_message)
        if raise_exception:
            raise Exception(error_message)
        if capture_output:
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            stdout_decoded = ansi_escape.sub('', stdout_decoded)
            stderr_decoded = ansi_escape.sub('', stderr_decoded)

            return stdout_decoded, stderr_decoded
        return None

    if capture_output:
        return stdout_decoded, stderr_decoded

    logger.debug(f"Command executed successfully: {command}")
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


async def remove_ansi_escape_codes(text: str) -> str:
    logger.debug(f"Removing ANSI escape codes from: {text[:100]}...")
    # Decode the escaped sequences
    try:
        text = codecs.decode(text, 'unicode_escape')
    except UnicodeDecodeError as e:
        logger.error(f"Error decoding text: {e}")
        # Handle the error or return the original text
        return text

    # Original ANSI escape code regex
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_text = ansi_escape.sub('', text)
    logger.debug(f"Cleaned text: {clean_text[:100]}...")

    return clean_text


async def read_file_async(file_path: str):
    try:
        async with aiofiles.open(file_path, mode='r') as file:
            content = await file.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


async def read_last_lines_async(file_path, line_count):
    lines = []
    async with aiofiles.open(file_path, 'r') as file:
        await file.seek(0, 2)
        buffer_size = 1024
        while len(lines) <= line_count:
            position = max(await file.tell() - buffer_size, 0)
            await file.seek(position)

            buffer = await file.read(buffer_size)
            lines = buffer.splitlines()

            if position == 0:
                break

            buffer_size *= 2

    return lines[-line_count:]


async def write_file_async(file_path: str, content: str) -> None:
    async with aiofiles.open(file_path, 'w') as f:
        await f.write(content)
