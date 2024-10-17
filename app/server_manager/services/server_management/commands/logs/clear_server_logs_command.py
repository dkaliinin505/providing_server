import logging

from utils.async_util import run_command_async
import os
from app.server_manager.interfaces.command_interface import Command

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ClearServerLogsCommand(Command):
    def __init__(self, config):
        self.config = config
        self.log_path = None

    async def execute(self, data):
        self.log_path = data.get('log_path')

        if not self.log_path:
            return {"message": "Log path not provided."}

        if not os.path.exists(self.log_path):
            return {"message": f"Log file at {self.log_path} not found."}

        try:
            command = f"sudo truncate -s 0 {self.log_path}"
            result, error_output = await run_command_async(command, capture_output=True)
            logging.debug(f"Result: {result}")
            return {
                "message": f"Logs at {self.log_path} cleared successfully."
            }
        except Exception as e:
            raise Exception({
                "message": f"Failed to clear logs at {self.log_path}: {str(e)}"
            })
