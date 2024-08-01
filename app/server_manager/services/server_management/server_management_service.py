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
