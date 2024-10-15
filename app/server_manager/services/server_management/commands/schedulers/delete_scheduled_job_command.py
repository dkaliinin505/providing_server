from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class DeleteScheduledJobCommand(Command):
    def __init__(self, config):
        self.user = None
        self.job_id = None
        self.config = config

    async def execute(self, data):
        self.config = data
        self.user = self.config.get('user')
        self.job_id = self.config.get('job_id')
        delete_command = f'crontab -l -u {self.user} | grep -v "# JOB_ID={self.job_id}" | crontab -u {self.user} -'

        result = await run_command_async(delete_command, capture_output=True)

        if result:
            return {"message": "Scheduled job deleted successfully"}
        else:
            return {"error": "Failed to delete scheduled job"}
