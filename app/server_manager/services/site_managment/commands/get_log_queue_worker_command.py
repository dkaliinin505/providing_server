import aiofiles
import logging
from pathlib import Path

from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GetQueueWorkerLogsCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config = data
        worker_id = self.config.get('worker_id')
        log_dir = Path(f"/home/{self.config.get('user', 'super_forge')}/.logs")
        log_file = Path(log_dir) / f"worker-{worker_id}.log"
        if await check_file_exists(log_file):
            async with aiofiles.open(log_file, 'r') as log_file:
                logs = await log_file.read()
                logging.debug(f"Logs for worker {log_file}: {logs}")
                return {"message": "Logs Retrieved Successfully", "data": logs}
        else:
            logging.error(f"Log file for worker {log_file} not found.")
            return {"error": f"Log file for worker {log_file} not found."}