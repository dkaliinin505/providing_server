import logging

from quart import jsonify

from app.server_manager.controllers.controller import Controller
from app.server_manager.services.site_managment.site_management_service import SiteManagementService
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.site_management.create_certbot_cert_schema import \
    CreateCertBotCertificateSchema
from app.server_manager.validators.schemas.site_management.delete_certbot_cert_schema import \
    DeleteCertBotCertificateSchema
from app.server_manager.validators.schemas.site_management.deploy_project_config_schema import DeployProjectSchema
from app.server_manager.validators.schemas.validation_schema import RequestSchema


class SiteManagementController(Controller):
    def __init__(self):
        super().__init__()
        self.site_management_service = SiteManagementService()

    @validate_request({'POST': DeployProjectSchema})
    async def deploy_project(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.deploy_project, data)
        return jsonify({"message": "Deploy Project Task started in background", "task_id": task_id}), 200

    @validate_request({'POST': CreateCertBotCertificateSchema})
    async def create_certbot_cert(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.create_certbot_cert, data)
        return jsonify({"message": "Create Certbot Certificate Task started in background", "task_id": task_id}), 200

    @validate_request({'DELETE': DeleteCertBotCertificateSchema})
    async def delete_certbot_cert(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.delete_certbot_cert, data)
        return jsonify({"message": "Delete Certbot Certificate Task started in background", "task_id": task_id}), 200

    @validate_request({'GET': RequestSchema})
    async def test(self, data):
        task_id = await self.task_manager.submit_task(self.site_management_service.test, data)
        logging.info(f"Test Task started in background with task_id: {task_id}")
        return {"message": "Test Task started in background", "task_id": task_id}

    def __del__(self):
        super().cleanup(resource_types=[SiteManagementService])
