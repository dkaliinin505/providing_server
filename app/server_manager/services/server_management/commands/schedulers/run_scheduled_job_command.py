from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class RunScheduledJobCommand(Command):
    def __init__(self, config):
        self.job_command = None
        self.config = config

    async def execute(self, data):
        self.config = data
        self.job_command = self.config.get('command')
        
        result = await run_command_async(self.job_command, capture_output=True)

        if result:
            return {"message": "Scheduled job executed successfully", "data": result[0]}
        else:
            return {"message": "Failed to execute scheduled job", "data": result[1]}
