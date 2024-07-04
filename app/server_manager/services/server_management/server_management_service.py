import logging

from app.server_manager.managers.task_manager import TaskManager
from app.server_manager.services.server_management.commands.create_site_command import CreateSiteCommand
from app.server_manager.services.server_management.commands.delete_deploy_key_command import DeleteDeployKeyCommand
from app.server_manager.services.server_management.commands.generate_deploy_key_command import GenerateDeployKeyCommand
from app.server_manager.services.server_management.commands.mysql.create_database_command import CreateDatabaseCommand
from app.server_manager.services.server_management.commands.mysql.create_database_user_command import \
    CreateDatabaseUserCommand
from app.server_manager.services.server_management.commands.mysql.delete_database_command import DeleteDatabaseCommand
from app.server_manager.services.server_management.commands.mysql.delete_database_user_command import \
    DeleteDatabaseUserCommand
from app.server_manager.services.server_management.commands.mysql.update_database_user_command import \
    UpdateDatabaseUserCommand
from app.server_manager.services.server_management.invoker import ServerManagementExecutor


class ServerManagementService:

    def __init__(self):
        self.task_manager = TaskManager()
        self.executor = ServerManagementExecutor()
        self.executor.register('create_site', CreateSiteCommand({'config': {}}))
        self.executor.register('generate_deploy_key', GenerateDeployKeyCommand({'config': {}}))
        self.executor.register('delete_deploy_key', DeleteDeployKeyCommand({'config': {}}))
        self.executor.register('create_database', CreateDatabaseCommand({'config': {}}))
        self.executor.register('create_database_user', CreateDatabaseUserCommand({'config': {}}))
        self.executor.register('update_database_user', UpdateDatabaseUserCommand({'config': {}}))
        self.executor.register('delete_database', DeleteDatabaseCommand({'config': {}}))
        self.executor.register('delete_database_user', DeleteDatabaseUserCommand({'config': {}}))

    async def generate_deploy_key(self, data):
        return self.executor.execute('generate_deploy_key', data)

    async def delete_deploy_key(self, data):
        return self.executor.execute('delete_deploy_key', data)

    async def create_site(self, data):
        data = await self.executor.execute('create_site', data)
        logging.info(f"Create Site Task in ServerManagementService started in background with task_id: {data}")
        return data

    async def create_database(self, data):
        return self.executor.execute('create_database', data)

    async def create_database_user(self, data):
        return self.executor.execute('create_database_user', data)

    async def update_database_user(self, data):
        return self.executor.execute('update_database_user', data)

    async def delete_database(self, data):
        return self.executor.execute('delete_database', data)

    async def delete_database_user(self, data):
        return self.executor.execute('delete_database_user', data)
