import aiofiles
import logging
from pathlib import Path

from app.server_manager.interfaces.command_interface import Command

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GetQueueWorkerInfoCommand(Command):
    def __init__(self, config):
        self.config = config
        self.supervisor_conf_dir = Path("/etc/supervisor/conf.d")

    async def execute(self, data):
        self.config = data
        return await self.get_worker_command()

    async def get_worker_command(self):
        worker_id = self.config.get('worker_id')
        conf_path = self.supervisor_conf_dir / f"worker-{worker_id}.conf"

        if not conf_path.exists():
            logging.error(f"Supervisor config file for worker {worker_id} not found.")
            return {"error": f"Supervisor config file for worker {worker_id} not found."}

        async with aiofiles.open(conf_path, 'r') as conf_file:
            config_content = await conf_file.read()

        for line in config_content.splitlines():
            if line.strip().startswith("command="):
                command = line.strip().split("command=")[1]
                logging.debug(f"Command for worker {worker_id} retrieved: {command}")
                return {"message": f"Command for worker {worker_id} retrieved", "data": command}

        logging.error(f"No command found in config file for worker {worker_id}.")
        return {"error": f"No command found in config file for worker {worker_id}."}
