from flask import jsonify

from app.server_manager.controllers.controller import Controller
from app.server_manager.services.site_managment.site_management_service import SiteManagementService
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.site_management.create_certbot_cert_schema import \
    CreateCertBotCertificateSchema
from app.server_manager.validators.schemas.site_management.delete_certbot_cert_schema import \
    DeleteCertBotCertificateSchema
from app.server_manager.validators.schemas.site_management.deploy_project_config_schema import DeployProjectSchema
from app.server_manager.validators.schemas.validation_schema import RequestSchema
from utils.env_util import update_env_variable
from utils.util import run_command


class SiteManagementController(Controller):
    def __init__(self):
        super().__init__()
        self.site_management_service = SiteManagementService()

    @validate_request({'POST': DeployProjectSchema})
    def deploy_project(self, data):
        result = self.site_management_service.deploy_project(data)
        return jsonify(result)

    @validate_request({'POST': CreateCertBotCertificateSchema})
    def create_certbot_cert(self, data):
        result = self.site_management_service.create_certbot_cert(data)
        return jsonify(result)

    @validate_request({'DELETE': DeleteCertBotCertificateSchema})
    def delete_certbot_cert(self, data):
        result = self.site_management_service.delete_certbot_cert(data)
        return jsonify(result)

    @validate_request({'GET': RequestSchema})
    def test(self, data):
        run_command("sudo cp env.example .env.development")
        run_command("sudo chown super_forge:super_forge .env.development")
        return jsonify({"message": "Site Management Controller is working"})

    def __del__(self):
        super().cleanup(resource_types=[SiteManagementService])
