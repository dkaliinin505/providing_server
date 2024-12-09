import logging

from app.server_manager.services.server_management.commands.schedulers.control_scheduled_job_command import \
    ControlScheduledJobCommand
from app.server_manager.services.server_management.commands.schedulers.create_scheduled_job_command import \
    CreateScheduledJobCommand
from app.server_manager.services.server_management.commands.schedulers.delete_scheduled_job_command import \
    DeleteScheduledJobCommand
from app.server_manager.services.server_management.commands.schedulers.get_scheduler_job_logs_command import \
    GetSchedulerLogCommand
from app.server_manager.services.server_management.commands.schedulers.run_scheduled_job_command import \
    RunScheduledJobCommand
from app.server_manager.services.server_management.commands.schedulers.update_scheduled_job_command import \
    UpdateScheduledJobCommand
from app.server_manager.services.service import Service


class SchedulerService(Service):
    def __init__(self):
        super().__init__()
        self.executor.register('create_scheduled_job', CreateScheduledJobCommand({'config': {}}))
        self.executor.register('update_scheduled_job', UpdateScheduledJobCommand({'config': {}}))
        self.executor.register('delete_scheduled_job', DeleteScheduledJobCommand({'config': {}}))
        self.executor.register('get_scheduler_job_logs', GetSchedulerLogCommand({'config': {}}))
        self.executor.register('control_scheduled_job', ControlScheduledJobCommand({'config': {}})),
        self.executor.register('run_scheduled_job', RunScheduledJobCommand({'config': {}}))

    async def create_scheduled_job(self, data):
        data = await self.executor.execute('create_scheduled_job', data)
        logging.info(f"Create Scheduled Job Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def update_scheduled_job(self, data):
        data = await self.executor.execute('update_scheduled_job', data)
        logging.info(f"Update Scheduled Job Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def delete_scheduled_job(self, data):
        data = await self.executor.execute('delete_scheduled_job', data)
        logging.info(f"Delete Scheduled Job Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def get_scheduler_job_logs(self, data):
        data = await self.executor.execute('get_scheduler_job_logs', data)
        logging.info(
            f"Get Scheduler Job Logs Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def run_scheduled_job(self, data):
        data = await self.executor.execute('run_scheduled_job', data)
        logging.info(f"Run Scheduled Job Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def control_scheduled_job(self, data):
        data = await self.executor.execute('control_scheduled_job', data)
        logging.info(
            f"Control Scheduled Job Task in ServerManagementService started in background with task_id: {data}")
        return data
