from app.server_manager.interfaces.command_interface import Command
from utils.async_util import read_file_async


class GetSchedulerLogCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        job_id = data.get('job_id')
        log_file_path = f"/var/log/scheduler_logs/{job_id}.log"

        log_content = await read_file_async(log_file_path)

        if "Error" in log_content:
            return {"error": f"Failed to read log for job_id {job_id}: {log_content}"}

        return {
            "message": f"Log for job_id {job_id}",
            "data": log_content
        }
