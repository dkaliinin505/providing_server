import logging

from app.server_manager.controllers.controller import Controller
from app.server_manager.services.site_managment.site_management_service import SiteManagementService


class SiteManagementController(Controller):
    def __init__(self):
        super().__init__()
        self.site_management_service = SiteManagementService()

    async def deploy_project(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.deploy_project, data)
        return {"message": "Deploy Project Task started in background", "task_id": task_id}

    async def create_certbot_cert(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.create_certbot_cert, data)
        return {"message": "Create Certbot Certificate Task started in background", "task_id": task_id}

    async def delete_certbot_cert(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.delete_certbot_cert, data)
        return {"message": "Delete Certbot Certificate Task started in background", "task_id": task_id}

    async def create_queue_worker(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.create_queue_worker, data)
        return {"message": "Create Queue Worker Task started in background", "task_id": task_id}

    async def delete_queue_worker(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.delete_queue_worker, data)
        return {"message": "Delete Queue Worker Task started in background", "task_id": task_id}

    async def restart_queue_worker(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.restart_queue_worker, data)
        return {"message": "Restart Queue Worker Task started in background", "task_id": task_id}

    async def get_queue_worker_logs(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.get_queue_worker_logs, data)
        return {"message": "Get Queue Worker Logs Task started in background", "task_id": task_id}

    async def test(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.test, data)
        logging.info(f"Test Task started in background with task_id: {task_id}")
        return {"message": "Test Task started in background", "task_id": task_id}

    def __del__(self):
        super().cleanup(resource_types=[SiteManagementService])
