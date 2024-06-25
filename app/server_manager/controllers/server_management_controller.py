from flask import jsonify

from app.server_manager.controllers.controller import Controller
from app.server_manager.services.package_installer.package_installer_service import PackageInstallerService
from app.server_manager.services.server_management.server_management_service import ServerManagementService
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.install_package_schema import InstallPackageSchema
from app.server_manager.validators.schemas.server_management.create_site_config_schema import CreateSiteSchema
from app.server_manager.validators.schemas.validation_schema import RequestSchema
from app.server_manager.validators.schemas.server_management.generate_deploy_key_config_schema import GenerateDeployKeyCommandSchema


class ServerManagementController(Controller):
    def __init__(self):
        super().__init__()
        self.server_management_service = ServerManagementService()
        self.package_installer_service = PackageInstallerService()

    @validate_request({'POST': GenerateDeployKeyCommandSchema})
    def generate_deploy_key(self, data):
        result = self.server_management_service.generate_deploy_key(data)
        return jsonify(result)

    @validate_request({'DELETE': GenerateDeployKeyCommandSchema})
    def delete_deploy_key(self, data):
        result = self.server_management_service.delete_deploy_key(data)
        return jsonify(result)

    @validate_request({'POST': CreateSiteSchema})
    def create_site(self, data):
        result = self.server_management_service.create_site(data)
        return jsonify(result)

    @validate_request({'POST': InstallPackageSchema})
    def install_package(self, data):
        result = self.package_installer_service.install_package(data)
        return jsonify(result)

    def __del__(self):
        super().cleanup(resource_types=[ServerManagementService, PackageInstallerService])
