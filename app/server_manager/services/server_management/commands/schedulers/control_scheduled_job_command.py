import os
import uuid
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class ControlScheduledJobCommand(Command):
    def __init__(self, config):
        self.config = config
        self.user = None
        self.job_id = None
        self.action = None

    async def execute(self, data, job_action='control'):
        self.config = data
        self.user = self.config.get('user')
        self.job_id = self.config.get('job_id')
        self.action = self.config.get('action')  # 'pause' или 'resume'

        # if not self.user or not self.job_id or not self.action:
        #     return {"error": "Missing required parameters: user, job_id, action"}


        pause_flag = f"/home/{self.user}/paused_jobs/{self.job_id}.pause"
        os.makedirs("/home/super_forge/paused_jobs", exist_ok=True)

        if self.action == 'pause':
            return await self.pause_job(pause_flag)
        elif self.action == 'resume':
            return await self.resume_job(pause_flag)

    async def pause_job(self, pause_flag):
        try:
            with open(pause_flag, 'w') as f:
                f.write('paused')
            print(f"Job {self.job_id} paused by creating flag {pause_flag}.")
            return {"message": f"Scheduled job paused successfully", "data": self.job_id}
        except Exception as e:
            print(f"Error pausing job {self.job_id}: {e}")
            raise Exception(f"Failed to pause job: {e}")

    async def resume_job(self, pause_flag):
        try:
            if os.path.exists(pause_flag):
                os.remove(pause_flag)
                print(f"Job {self.job_id} resumed by removing flag {pause_flag}.")
                return {"message": f"Scheduled job resumed successfully", "data": self.job_id}
            else:
                print(f"No pause flag found for job {self.job_id}. Job is not paused.")
                return {"message": "Job is not paused."}
        except Exception as e:
            print(f"Error resuming job {self.job_id}: {e}")
            raise Exception(f"Failed to resume job: {e}")