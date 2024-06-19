from app.server_manager.services.server_management.commands.create_site_command import CreateSiteCommand
from app.server_manager.services.server_management.commands.delete_deploy_key_command import DeleteDeployKeyCommand
from app.server_manager.services.server_management.commands.generate_deploy_key_command import GenerateDeployKeyCommand
from app.server_manager.services.server_management.invoker import ServerManagementExecutor


class ServerManagementService:

    def __init__(self):
        self.executor = ServerManagementExecutor()
        self.executor.register('create_site', CreateSiteCommand({'config': {}}))
        self.executor.register('generate_deploy_key', GenerateDeployKeyCommand({'config': {}}))
        self.executor.register('delete_deploy_key', DeleteDeployKeyCommand({'config': {}}))

    def generate_deploy_key(self, data):
        return self.executor.execute('generate_deploy_key', data)

    def delete_deploy_key(self, data):
        return self.executor.execute('delete_deploy_key', data)

    def create_site(self, data):
        return self.executor.execute('create_site', data)

    def install_application(self, data):
        return {"message": "Action 2 completed"}
