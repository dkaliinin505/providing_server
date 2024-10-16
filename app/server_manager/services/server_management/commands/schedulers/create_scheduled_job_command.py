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
        self.job_id = str(uuid.uuid4())  # Ensure job_id is generated and assigned correctly

        # Define log file path
        log_file = f"/home/super_forge/logs/{self.job_id}.log"
        os.makedirs("/home/super_forge/logs", exist_ok=True)
        full_command = f"{self.command} > {log_file} 2>&1"

        # Generate cron expression based on frequency
        cron_expression = await self.generate_cron_expression()

        if not cron_expression:
            return {"error": "Invalid frequency or custom schedule"}

        # Use cron_expression instead of frequency in the crontab command
        cron_command = f'(crontab -l -u {self.user} 2>/dev/null | grep -v "# JOB_ID={self.job_id}"; echo "{cron_expression} {full_command} # JOB_ID={self.job_id}") | crontab -u {self.user} -'

        # Execute the crontab update command
        result = await run_command_async(cron_command, capture_output=True)

        if result:
            return {"message": f"Scheduled job created successfully", "data": self.job_id}
        else:
            raise Exception(f"Failed to create scheduled job")

    async def generate_cron_expression(self):
        """Generate the correct cron expression based on the frequency or custom schedule."""
        if self.frequency == 'custom':
            custom_schedule = self.config.get('custom_schedule')

            # Extract custom schedule values
            minute = custom_schedule.get('minute', '*')
            hour = custom_schedule.get('hour', '*')
            day_of_week = custom_schedule.get('day_of_week', '*')
            day_of_month = custom_schedule.get('day_of_month', '*')
            month = custom_schedule.get('month', '*')

            # Return the cron expression
            return f"{minute} {hour} {day_of_month} {month} {day_of_week}"

        # Predefined frequencies
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
