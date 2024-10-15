import os
import uuid
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class CreateScheduledJobCommand(Command):
    def __init__(self, config):
        self.config = config
        self.user = None
        self.job_id = None
        self.command = None
        self.frequency = None
        self.custom_schedule = None

    async def execute(self, data, job_action='create'):
        self.config = data
        self.user = self.config.get('user')
        self.command = self.config.get('command')
        self.frequency = self.config.get('frequency')
        job_id = str(uuid.uuid4())

        log_file = f"/home/super_forge/logs/{self.job_id}.log"
        os.makedirs("/home/super_forge/logs", exist_ok=True)
        full_command = f"{self.command} >> {log_file} 2>&1"

        cron_expression = await self.generate_cron_expression()

        if not cron_expression:
            return {"error": "Invalid frequency or custom schedule"}

        cron_command = f'(crontab -l -u {self.user} | grep -v "# JOB_ID={job_id}"; echo "{self.frequency} {full_command} # JOB_ID={self.job_id}") | crontab -u {self.user} -'

        result = await run_command_async(cron_command, capture_output=True)

        if result:
            return {"message": f"Scheduled job created successfully"}
        else:
            raise Exception(f"Failed to create scheduled job")

    async def generate_cron_expression(self):
        if self.frequency == 'custom':
            custom_schedule = self.config.get('custom_schedule')

            minute = custom_schedule['minute']
            hour = custom_schedule['hour']
            day_of_week = custom_schedule['day_of_week']
            day_of_month = custom_schedule['day_of_month']
            month = custom_schedule('month', '*')
            return f"{minute} {hour} {day_of_month} {month} {day_of_week}"

        if self.frequency == 'Every Minute':
            return "* * * * *"
        elif self.frequency == 'Hourly':
            return "0 * * * *"
        elif self.frequency == 'Nightly':
            return "0 0 * * *"
        elif self.frequency == 'Weekly':
            return "0 0 * * 0"
        elif self.frequency == 'Monthly':
            return "0 0 1 * *"
        elif self.frequency == 'On Reboot':
            return "@reboot"
        else:
            return None
