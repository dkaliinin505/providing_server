import logging

from app.server_manager.managers.task_manager import TaskManager
from app.server_manager.services.server_management.commands.create_site_command import CreateSiteCommand
from app.server_manager.services.server_management.commands.delete_deploy_key_command import DeleteDeployKeyCommand
from app.server_manager.services.server_management.commands.delete_site_command import DeleteSiteCommand
from app.server_manager.services.server_management.commands.generate_deploy_key_command import GenerateDeployKeyCommand
from app.server_manager.services.server_management.commands.mysql.create_database_command import CreateDatabaseCommand
from app.server_manager.services.server_management.commands.mysql.create_database_user_command import \
    CreateDatabaseUserCommand
from app.server_manager.services.server_management.commands.mysql.delete_database_command import DeleteDatabaseCommand
from app.server_manager.services.server_management.commands.mysql.delete_database_user_command import \
    DeleteDatabaseUserCommand
from app.server_manager.services.server_management.commands.mysql.update_database_user_command import \
    UpdateDatabaseUserCommand
from app.server_manager.services.invoker import CommandExecutor
from app.server_manager.services.server_management.commands.php.php_config_update_command import PhpConfigUpdateCommand
from app.server_manager.services.server_management.commands.php.php_get_config_file_command import \
    PhpGetConfigFileCommand
from app.server_manager.services.server_management.commands.php.php_toggle_opcache_command import \
    PhpOpcacheToggleCommand
from app.server_manager.services.server_management.commands.php.php_update_config_file_command import \
    PhpConfigUpdateFileCommand
from app.server_manager.services.server_management.commands.php.php_version_delete_command import \
    PhpVersionDeleteCommand
from app.server_manager.services.server_management.commands.php.php_version_install_command import \
    PhpVersionInstallCommand
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


class ServerManagementService(Service):

    def __init__(self):
        super().__init__()
        self.task_manager = TaskManager()
        self.executor.register('create_site', CreateSiteCommand({'config': {}}))
        self.executor.register('delete_site', DeleteSiteCommand({'config': {}}))
        self.executor.register('generate_deploy_key', GenerateDeployKeyCommand({'config': {}}))
        self.executor.register('delete_deploy_key', DeleteDeployKeyCommand({'config': {}}))
        self.executor.register('create_database', CreateDatabaseCommand({'config': {}}))
        self.executor.register('create_database_user', CreateDatabaseUserCommand({'config': {}}))
        self.executor.register('update_database_user', UpdateDatabaseUserCommand({'config': {}}))
        self.executor.register('delete_database', DeleteDatabaseCommand({'config': {}}))
        self.executor.register('delete_database_user', DeleteDatabaseUserCommand({'config': {}}))
        self.executor.register('php_version_install', PhpVersionInstallCommand({'config': {}}))
        self.executor.register('php_config_update', PhpConfigUpdateCommand({'config': {}}))
        self.executor.register('php_toggle_opcache', PhpOpcacheToggleCommand({'config': {}}))
        self.executor.register('php_update_config_file', PhpConfigUpdateFileCommand({'config': {}}))
        self.executor.register('php_get_config_file', PhpGetConfigFileCommand({'config': {}}))
        self.executor.register('php_version_delete', PhpVersionDeleteCommand({'config': {}}))
        self.executor.register('create_scheduled_job', CreateScheduledJobCommand({'config': {}}))
        self.executor.register('update_scheduled_job', UpdateScheduledJobCommand({'config': {}}))
        self.executor.register('delete_scheduled_job', DeleteScheduledJobCommand({'config': {}}))
        self.executor.register('get_scheduler_job_logs', GetSchedulerLogCommand({'config': {}}))
        self.executor.register('run_scheduled_job', RunScheduledJobCommand({'config': {}}))

    async def generate_deploy_key(self, data):
        data = await self.executor.execute('generate_deploy_key', data)
        logging.info(f"Generate Deploy Key Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def delete_deploy_key(self, data):
        data = await self.executor.execute('delete_deploy_key', data)
        logging.info(f"Delete Deploy Key Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def create_site(self, data):
        data = await self.executor.execute('create_site', data)
        logging.info(f"Create Site Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def delete_site(self, data):
        data = await self.executor.execute('delete_site', data)
        logging.info(f"Delete Site Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def create_database(self, data):
        data = await self.executor.execute('create_database', data)
        logging.info(f"Create Database Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def create_database_user(self, data):
        data = await self.executor.execute('create_database_user', data)
        logging.info(f"Create Database User Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def update_database_user(self, data):
        data = await self.executor.execute('update_database_user', data)
        logging.info(f"Update Database User Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def delete_database(self, data):
        data = await self.executor.execute('delete_database', data)
        logging.info(f"Delete Database Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def delete_database_user(self, data):
        data = await self.executor.execute('delete_database_user', data)
        logging.info(f"Delete Database User Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def php_version_install(self, data):
        data = await self.executor.execute('php_version_install', data)
        logging.info(f"PHP Version Install Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def php_config_update(self, data):
        data = await self.executor.execute('php_config_update', data)
        logging.info(f"PHP Config Update Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def php_toggle_opcache(self, data):
        data = await self.executor.execute('php_toggle_opcache', data)
        logging.info(f"PHP Toggle Opcache Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def php_update_config_file(self, data):
        data = await self.executor.execute('php_update_config_file', data)
        logging.info(f"PHP Update Config File Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def php_get_config_file(self, data):
        data = await self.executor.execute('php_get_config_file', data)
        logging.info(f"PHP Get Config File Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def php_version_delete(self, data):
        data = await self.executor.execute('php_version_delete', data)
        logging.info(f"PHP Version Delete Task in ServerManagementService started in background with task_id: {data}")
        return data

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
        logging.info(f"Get Scheduler Job Logs Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def run_scheduled_job(self, data):
        data = await self.executor.execute('run_scheduled_job', data)
        logging.info(f"Run Scheduled Job Task in ServerManagementService started in background with task_id: {data}")
        return data

