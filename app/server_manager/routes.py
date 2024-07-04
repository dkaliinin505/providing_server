import logging

from quart import Blueprint, jsonify

from app.server_manager.controllers.controller import Controller
from app.server_manager.controllers.server_management_controller import ServerManagementController
from app.server_manager.controllers.site_management_controller import SiteManagementController

server_manager_blueprint = Blueprint('server_manager', __name__)
task_manager = Controller().task_manager
server_management_controller = ServerManagementController()
site_management_controller = SiteManagementController()


@server_manager_blueprint.route('/generate-deploy-key', methods=['POST'])
def generate_deploy_key_route():
    return server_management_controller.generate_deploy_key()


@server_manager_blueprint.route('/delete-deploy-key', methods=['DELETE'])
def delete_deploy_key_route():
    return server_management_controller.delete_deploy_key()


@server_manager_blueprint.route('/create-site', methods=['POST'])
async def create_site_route():
    data = await server_management_controller.create_site()
    return data


@server_manager_blueprint.route('/install-package', methods=['POST'])
def install_package_route():
    return server_management_controller.install_package()


@server_manager_blueprint.route('/deploy-project', methods=['POST'])
async def deploy_project_route():
    return await site_management_controller.deploy_project()


@server_manager_blueprint.route('/create-certbot-cert', methods=['POST'])
async def create_certbot_cert_route():
    return await site_management_controller.create_certbot_cert()


@server_manager_blueprint.route('/delete-certbot-cert', methods=['DELETE'])
async def delete_certbot_cert_route():
    return await site_management_controller.delete_certbot_cert()


@server_manager_blueprint.route('/create-database', methods=['POST'])
def create_database_route():
    return server_management_controller.create_database()


@server_manager_blueprint.route('/create-database-user', methods=['POST'])
def create_database_user_route():
    return server_management_controller.create_database_user()


@server_manager_blueprint.route('/delete-database', methods=['DELETE'])
def delete_database_route():
    return server_management_controller.delete_database()


@server_manager_blueprint.route('/delete-database-user', methods=['DELETE'])
def delete_database_user_route():
    return server_management_controller.delete_database_user()


@server_manager_blueprint.route('/update-database-user', methods=['PUT'])
def update_database_user_route():
    return server_management_controller.update_database_user()


@server_manager_blueprint.route('/test', methods=['GET'])
async def test_route():
    data = await site_management_controller.test()
    logging.info("Returned task id from controller method" + str(data))
    return jsonify(data)


@server_manager_blueprint.route('/task-status/<int:task_id>', methods=['GET'])
async def task_status_route(task_id):
    status = await task_manager.get_task_status(task_id)
    logging.info(f"Status for Task ID {task_id}: {status}")
    return jsonify(status)
