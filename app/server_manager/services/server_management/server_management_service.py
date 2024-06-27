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
        self.executor = ServerManagementExecutor()
        self.executor.register('create_site', CreateSiteCommand({'config': {}}))
        self.executor.register('generate_deploy_key', GenerateDeployKeyCommand({'config': {}}))
        self.executor.register('delete_deploy_key', DeleteDeployKeyCommand({'config': {}}))
        self.executor.register('create_database', CreateDatabaseCommand({'config': {}}))
        self.executor.register('create_database_user', CreateDatabaseUserCommand({'config': {}}))
        self.executor.register('update_database_user', UpdateDatabaseUserCommand({'config': {}}))
        self.executor.register('delete_database', DeleteDatabaseCommand({'config': {}}))
        self.executor.register('delete_database_user', DeleteDatabaseUserCommand({'config': {}}))

    def generate_deploy_key(self, data):
        return self.executor.execute('generate_deploy_key', data)

    def delete_deploy_key(self, data):
        return self.executor.execute('delete_deploy_key', data)

    def create_site(self, data):
        return self.executor.execute('create_site', data)

    def create_database(self, data):
        return self.executor.execute('create_database', data)

    def create_database_user(self, data):
        return self.executor.execute('create_database_user', data)

    def update_database_user(self, data):
        return self.executor.execute('update_database_user', data)

    def delete_database(self, data):
        return self.executor.execute('delete_database', data)

    def delete_database_user(self, data):
        return self.executor.execute('delete_database_user', data)
