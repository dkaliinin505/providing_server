from app.server_manager.services.server_management.commands.create_site_command import CreateSiteCommand
from app.server_manager.services.server_management.invoker import ServerManagementExecutor
from app.server_manager.services.service import Service
from app.server_manager.services.site_managment.commands.create_certbot_cert_command import \
    CreateCertBotCertificateCommand
from app.server_manager.services.site_managment.commands.delete_certbot_cert_command import DeleteCertBotCertCommand
from app.server_manager.services.site_managment.commands.deploy_project_command import DeployProjectCommand


class SiteManagementService(Service):

    def __init__(self):
        super().__init__()
        self.executor.register('deploy_project', DeployProjectCommand({'config': {}}))
        self.executor.register('create_certbot_cert', CreateCertBotCertificateCommand({'config': {}}))
        self.executor.register('delete_certbot_cert', DeleteCertBotCertCommand({'config': {}}))

    def deploy_project(self, data):
        return self.executor.execute('deploy_project', data)

    def create_certbot_cert(self, data):
        return self.executor.execute('create_certbot_cert', data)

    def delete_certbot_cert(self, data):
        return self.executor.execute('delete_certbot_cert', data)
