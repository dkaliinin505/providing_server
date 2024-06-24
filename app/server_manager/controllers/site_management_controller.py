from flask import jsonify

from app.server_manager.services.site_managment.site_management_service import SiteManagementService
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.site_management.create_certbot_cert_schema import \
    CreateCertBotCertificateSchema
from app.server_manager.validators.schemas.site_management.deploy_project_config_schema import DeployProjectSchema


class SiteManagementController:
    def __init__(self):
        self.site_management_service = SiteManagementService()

    @validate_request({'POST': DeployProjectSchema})
    def deploy_project(self, data):
        result = self.site_management_service.deploy_project(data)
        return jsonify(result)

    @validate_request({'POST': CreateCertBotCertificateSchema})
    def create_certbot_cert(self, data):
        result = self.site_management_service.create_certbot_cert(data)
        return jsonify(result)
