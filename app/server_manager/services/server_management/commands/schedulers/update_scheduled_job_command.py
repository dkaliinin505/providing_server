from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class UpdateScheduledJobCommand(Command):
    def __init__(self, config):
        self.config = config
        self.user = None
        self.job_id = None
        self.command = None
        self.frequency = None
        self.custom_schedule = None

    async def execute(self, data, job_action='update'):
        self.config = data
        self.user = self.config.get('user')
        self.job_id = self.config.get('job_id')  # job_id is required for update
        self.command = self.config.get('command')
        self.frequency = self.config.get('frequency')

        log_file = f"/home/super_forge/logs/{self.job_id}.log"
        full_command = f"{self.command} >> {log_file} 2>&1"

        # Generate the cron expression based on the frequency or custom schedule
        cron_expression = await self.generate_cron_expression()
        if not cron_expression:
            return {"error": "Invalid frequency or custom schedule"}

        # Find and remove the old job by job_id
        remove_old_job_command = f'(crontab -l -u {self.user} 2>/dev/null | grep -v "# JOB_ID={self.job_id}") | crontab -u {self.user} -'
        await run_command_async(remove_old_job_command, capture_output=True)

        # Add the updated job with the new cron expression
        cron_command = f'(crontab -l -u {self.user} 2>/dev/null; echo "{cron_expression} {full_command} # JOB_ID={self.job_id}") | crontab -u {self.user} -'
        result = await run_command_async(cron_command, capture_output=True)

        if result:
            return {"message": f"Scheduled job with ID {self.job_id} updated successfully"}
        else:
            return {"error": f"Failed to update scheduled job"}

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
