import logging

from quart import jsonify

from app.server_manager.controllers.controller import Controller
from app.server_manager.services.package_installer.package_installer_service import PackageInstallerService
from app.server_manager.services.server_management.server_management_service import ServerManagementService
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.install_package_schema import InstallPackageSchema
from app.server_manager.validators.schemas.server_management.create_site_config_schema import CreateSiteSchema
from app.server_manager.validators.schemas.server_management.mysql.create_database_schema import CreateDatabaseSchema
from app.server_manager.validators.schemas.server_management.mysql.create_database_user_schema import \
    CreateDatabaseUserSchema
from app.server_manager.validators.schemas.server_management.mysql.delete_database_schema import DeleteDatabaseSchema
from app.server_manager.validators.schemas.server_management.mysql.delete_database_user_config import \
    DeleteDatabaseUserSchema
from app.server_manager.validators.schemas.server_management.generate_deploy_key_config_schema import \
    GenerateDeployKeyCommandSchema


class ServerManagementController(Controller):
    def __init__(self):
        super().__init__()
        self.server_management_service = ServerManagementService()
        self.package_installer_service = PackageInstallerService()

    @validate_request({'POST': GenerateDeployKeyCommandSchema})
    async def generate_deploy_key(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.generate_deploy_key, data)
        logging.info(f"Generate Deploy Key Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Generate Deploy Key Task started in background", "task_id": task_id}

    @validate_request({'DELETE': GenerateDeployKeyCommandSchema})
    async def delete_deploy_key(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_deploy_key, data)
        logging.info(f"Delete Deploy Key Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Delete Deploy Key Task started in background", "task_id": task_id}

    @validate_request({'POST': CreateSiteSchema})
    async def create_site(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.create_site, data)
        logging.info(f"Create Site Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Create Site Task started in background", "task_id": task_id}

    @validate_request({'POST': InstallPackageSchema})
    async def install_package(self, data):
        task_id = await self.task_manager.submit_task(self.package_installer_service.install_package, data)
        logging.info(f"Install Package Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Install Package Task started in background", "task_id": task_id}

    @validate_request({'POST': CreateDatabaseSchema})
    async def create_database(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.create_database, data)
        logging.info(f"Create Database Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Create database started in background", "task_id": task_id}

    @validate_request({'POST': CreateDatabaseUserSchema})
    async def create_database_user(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.create_database_user, data)
        logging.info(f"Create Database User Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Create database User task started in background", "task_id": task_id}

    @validate_request({'DELETE': DeleteDatabaseSchema})
    async def delete_database(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_database, data)
        logging.info(f"Delete Database Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Database delete task started in background", "task_id": task_id}

    @validate_request({'DELETE': DeleteDatabaseUserSchema})
    async def delete_database_user(self, data):
        logging.info(f"Delete Database User Task in ServerManagementController started with data: {data}")
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_database_user, data)
        logging.info(f"Delete Database User Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Delete database user task started in background", "task_id": task_id}

    @validate_request({'PUT': CreateDatabaseUserSchema})
    async def update_database_user(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.update_database_user, data)
        logging.info(f"Update Database User Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Updated database user task started in background", "task_id": task_id}

    def __del__(self):
        super().cleanup(resource_types=[ServerManagementService, PackageInstallerService])
