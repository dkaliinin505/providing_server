from utils.async_util import run_command_async
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
            command = f"sudo tail -n 500 {self.log_path}"
            logs, error_output = await run_command_async(command, capture_output=True)

            if logs:
                return {
                    "message": f"Last 500 lines of logs retrieved from {self.log_path}.",
                    "data": logs
                }
            else:
                return {
                    "error": f"Failed to retrieve logs: {error_output}"
                }
        except Exception as e:
            return {
                "error": f"Failed to retrieve logs from {self.log_path}: {str(e)}"
            }
