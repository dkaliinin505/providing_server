import aiofiles
import os
from app.server_manager.interfaces.command_interface import Command

class GetServerLogsCommand(Command):
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
            async with aiofiles.open(self.log_path, mode='r') as log_file:
                logs = await log_file.readlines()

            last_500_lines = logs[-500:] if len(logs) > 500 else logs
            return {
                "message": f"Last 500 lines of logs retrieved from {self.log_path}.",
                "data": ''.join(last_500_lines)
            }
        except Exception as e:
            return {
                "error": f"Failed to retrieve logs from {self.log_path}: {str(e)}"
            }
