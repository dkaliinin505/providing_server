import aiofiles
import logging
from pathlib import Path

from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DeleteQueueWorkerCommand(Command):
    def __init__(self, config):
        self.config = config
        self.supervisor_conf_dir = Path("/etc/supervisor/conf.d")

    async def execute(self, data):
        self.config = data
        worker_id = self.config.get('worker_id')
        await run_command_async(f"sudo supervisorctl stop worker-{worker_id}:*")
        logging.debug(f"Worker {worker_id} stopped.")

        conf_path = self.supervisor_conf_dir / f"worker-{worker_id}.conf"
        if await check_file_exists(conf_path):
            await run_command_async(f"sudo rm {conf_path}")
            logging.debug(f"Worker config for {worker_id} removed.")

        await run_command_async("sudo supervisorctl reread")
        await run_command_async("sudo supervisorctl update")
        logging.debug(f"Worker {worker_id} deleted from Supervisor.")
        return {"message": f"Worker {worker_id} deleted successfully."}
