import asyncio
import logging
import time

from app.server_manager.services.service import Service
from app.server_manager.services.site_managment.commands.create_certbot_cert_command import \
    CreateCertBotCertificateCommand
from app.server_manager.services.site_managment.commands.create_queue_worker_command import CreateQueueWorkerCommand
from app.server_manager.services.site_managment.commands.delete_certbot_cert_command import DeleteCertBotCertCommand
from app.server_manager.services.site_managment.commands.delete_queue_worker_command import DeleteQueueWorkerCommand
from app.server_manager.services.site_managment.commands.deploy_project_command import DeployProjectCommand
from app.server_manager.services.site_managment.commands.get_log_queue_worker_command import GetQueueWorkerLogsCommand
from app.server_manager.services.site_managment.commands.reboot_queue_worker_command import RestartQueueWorkerCommand
from utils.async_util import run_command_async, check_file_exists, dir_exists


class SiteManagementService(Service):

    def __init__(self):
        super().__init__()
        self.executor.register('deploy_project', DeployProjectCommand({'config': {}}))
        self.executor.register('create_certbot_cert', CreateCertBotCertificateCommand({'config': {}}))
        self.executor.register('delete_certbot_cert', DeleteCertBotCertCommand({'config': {}}))
        self.executor.register('create_queue_worker', CreateQueueWorkerCommand({'config': {}}))
        self.executor.register('delete_queue_worker', DeleteQueueWorkerCommand({'config': {}}))
        self.executor.register('restart_queue_worker', RestartQueueWorkerCommand({'config': {}}))
        self.executor.register('get_queue_worker_logs', GetQueueWorkerLogsCommand({'config': {}}))

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

    async def create_queue_worker(self, data):
        data = await self.executor.execute('create_queue_worker', data)
        logging.info(f"Create Queue Worker Task in SiteManagementService started in background with task_id: {data}")
        return data

    async def delete_queue_worker(self, data):
        data = await self.executor.execute('delete_queue_worker', data)
        logging.info(f"Delete Queue Worker Task in SiteManagementService started in background with task_id: {data}")
        return data

    async def restart_queue_worker(self, data):
        data = await self.executor.execute('restart_queue_worker', data)
        logging.info(f"Restart Queue Worker Task in SiteManagementService started in background with task_id: {data}")
        return data

    async def get_queue_worker_logs(self, data):
        data = await self.executor.execute('get_queue_worker_logs', data)
        logging.info(f"Get Queue Worker Logs Task in SiteManagementService started in background with task_id: {data}")
        return data

    async def test(self, data):
        logging.info("Test Task started")
        await asyncio.sleep(15)
        await run_command_async("sudo cp env.example .env.development", False)
        await run_command_async("sudo chown super_forge:super_forge .env.development", False)
        await asyncio.sleep(15)
        await run_command_async("sudo ls -ll")
        logging.info("Test Task completed")
        return {"message": "Site Management Service is working"}
