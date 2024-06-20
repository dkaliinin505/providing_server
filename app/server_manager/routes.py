from flask import Blueprint
from app.server_manager.controllers.server_management_controller import ServerManagementController
from app.server_manager.controllers.site_management_controller import SiteManagementController

server_manager_blueprint = Blueprint('server_manager', __name__)
server_management_controller = ServerManagementController()
site_management_controller = SiteManagementController()


@server_manager_blueprint.route('/generate-deploy-key', methods=['POST'])
def generate_deploy_key_route():
    return server_management_controller.generate_deploy_key()


@server_manager_blueprint.route('/delete-deploy-key', methods=['DELETE'])
def delete_deploy_key_route():
    return server_management_controller.delete_deploy_key()


@server_manager_blueprint.route('/create-site', methods=['POST'])
def create_site_route():
    return server_management_controller.create_site()


@server_manager_blueprint.route('/install-package', methods=['POST'])
def install_package_route():
    return server_management_controller.install_package()


@server_manager_blueprint.route('/deploy-application', methods=['POST'])
def deploy_application_route():
    return site_management_controller.deploy_project()
