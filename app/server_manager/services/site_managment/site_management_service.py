from app.server_manager.services.server_management.commands.create_site_command import CreateSiteCommand
from app.server_manager.services.server_management.invoker import ServerManagementExecutor
from app.server_manager.services.site_managment.commands.deploy_project_command import DeployProjectCommand


class SiteManagementService:

    def __init__(self):
        self.executor = ServerManagementExecutor()
        self.executor.register('deploy_project', DeployProjectCommand({'config': {}}))

    def deploy_project(self, data):
        return self.executor.execute('deploy_project', data)
