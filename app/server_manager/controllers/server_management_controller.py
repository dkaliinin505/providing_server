from flask import jsonify
from app.server_manager.services.package_installer.package_installer_service import PackageInstallerService
from app.server_manager.services.server_management.server_management_service import ServerManagementService
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.install_package_schema import InstallPackageSchema
from app.server_manager.validators.schemas.validation_schema import RequestSchema, AnotherRequestSchema


class ServerManagementController:
    def __init__(self):
        self.server_management_service = ServerManagementService()
        self.package_installer_service = PackageInstallerService()

    @validate_request({'POST': RequestSchema})
    def action1(self, data):
        result = self.server_management_service.action1(data)
        return jsonify(result)

    @validate_request({'POST': AnotherRequestSchema})
    def action2(self, data):
        result = self.server_management_service.action2(data)
        return jsonify(result)

    @validate_request({'POST': InstallPackageSchema})
    def install_package(self, data):
        result = self.package_installer_service.install_package(data)
        return jsonify(result)
