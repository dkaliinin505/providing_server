import asyncio
import logging

import aiofiles
from aiofiles import os


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