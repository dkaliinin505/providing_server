from app.server_manager.services.server_management.commands.create_site_command import CreateSiteCommand
from app.server_manager.services.server_management.invoker import ServerManagementExecutor


class ServerManagementService:

    def __init__(self):
        self.executor = ServerManagementExecutor()
        self.executor.register('create_site', CreateSiteCommand({'config': {}}))

    def create_site(self, data):
        return self.executor.execute('create_site', data)

    def install_application(self, data):
        return {"message": "Action 2 completed"}
