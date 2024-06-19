from flask import Blueprint
from app.server_manager.controllers.server_management_controller import ServerManagementController

server_manager_blueprint = Blueprint('server_manager', __name__)
controller = ServerManagementController()


@server_manager_blueprint.route('/generate-deploy-key', methods=['POST'])
def generate_deploy_key_route():
    return controller.generate_deploy_key()


@server_manager_blueprint.route('/delete-deploy-key', methods=['DELETE'])
def delete_deploy_key_route():
    return controller.delete_deploy_key()


@server_manager_blueprint.route('/create-site', methods=['POST'])
def create_site_route():
    return controller.create_site()


@server_manager_blueprint.route('/install-package', methods=['POST'])
def install_package_route():
    return controller.install_package()
