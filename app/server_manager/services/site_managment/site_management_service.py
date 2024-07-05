import asyncio
import logging
import time

from app.server_manager.services.service import Service
from app.server_manager.services.site_managment.commands.create_certbot_cert_command import \
    CreateCertBotCertificateCommand
from app.server_manager.services.site_managment.commands.delete_certbot_cert_command import DeleteCertBotCertCommand
from app.server_manager.services.site_managment.commands.deploy_project_command import DeployProjectCommand
from utils.util import run_command_async


class SiteManagementService(Service):

    def __init__(self):
        super().__init__()
        self.executor.register('deploy_project', DeployProjectCommand({'config': {}}))
        self.executor.register('create_certbot_cert', CreateCertBotCertificateCommand({'config': {}}))
        self.executor.register('delete_certbot_cert', DeleteCertBotCertCommand({'config': {}}))

    async def deploy_project(self, data):
        data = await self.executor.execute('deploy_project', data)
        logging.info(f"Deploy Project Task in SiteManagementService started in background with task_id: {data}")
        return data

    async def create_certbot_cert(self, data):
        data = await self.executor.execute('create_certbot_cert', data)
        logging.info(f"Create Certbot Cert Task in SiteManagementService started in background with task_id: {data}")
        return data

    async def delete_certbot_cert(self, data):
        data = await self.executor.execute('delete_certbot_cert', data)
        logging.info(f"Delete Certbot Cert Task in SiteManagementService started in background with task_id: {data}")
        return data

    async def test(self, data):
        logging.info("Test Task started")
        await asyncio.sleep(15)
        await run_command_async("sudo cp env.example .env.development", False)
        await run_command_async("sudo chown super_forge:super_forge .env.development",False)
        await asyncio.sleep(15)
        await run_command_async("sudo ls -ll")
        logging.info("Test Task completed")
        return {"message": "Site Management Service is working"}
