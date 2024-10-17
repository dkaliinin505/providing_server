import aiofiles
import os
from app.server_manager.interfaces.command_interface import Command


class ClearServerLogsCommand(Command):
    def __init__(self, config):
        self.config = config
        self.log_path = None

    async def execute(self, data):
        self.log_path = data.get('log_path')

        if not self.log_path:
            return {"error": "Log path not provided."}

        if not os.path.exists(self.log_path):
            return {"error": f"Log file at {self.log_path} not found."}

        try:
            async with aiofiles.open(self.log_path, mode='w') as log_file:
                await log_file.write('')

            return {
                "message": f"Log file at {self.log_path} cleared successfully."
            }
        except Exception as e:
            return {
                "error": f"Failed to clear logs at {self.log_path}: {str(e)}"
            }
