from flask import jsonify

from app.server_manager.services.site_managment.site_management_service import SiteManagementService
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.site_management.deploy_project_config_schema import DeploySiteSchema


class SiteManagementController:
    def __init__(self):
        self.site_management_service = SiteManagementService()

    @validate_request({'POST': DeployProjectSchema})
    def deploy_project(self, data):
        result = self.site_management_service.deploy_project(data)
        return jsonify(result)
