import aiofiles
import logging
from pathlib import Path

from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RestartQueueWorkerCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config = data
        worker_id = self.config.get('worker_id')
        await run_command_async(f"sudo supervisorctl restart worker-{worker_id}:*")
        logging.debug(f"Worker {worker_id} restarted.")
        return {"message": f"Worker {worker_id} restarted successfully."}
