import logging

from quart import Blueprint, jsonify

from app.server_manager.controllers.controller import Controller
from app.server_manager.controllers.server_management_controller import ServerManagementController
from app.server_manager.controllers.site_management_controller import SiteManagementController
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.server_management.mysql.create_database_user_schema import \
    CreateDatabaseUserSchema

server_manager_blueprint = Blueprint('server_manager', __name__)
task_manager = Controller().task_manager
server_management_controller = ServerManagementController()
site_management_controller = SiteManagementController()


@server_manager_blueprint.route('/generate-deploy-key', methods=['POST'])
async def generate_deploy_key_route():
    data = await server_management_controller.generate_deploy_key()
    return jsonify(data)


@server_manager_blueprint.route('/delete-deploy-key', methods=['DELETE'])
async def delete_deploy_key_route():
    data = await server_management_controller.delete_deploy_key()
    return jsonify(data)


@server_manager_blueprint.route('/create-site', methods=['POST'])
async def create_site_route():
    data = await server_management_controller.create_site()
    return jsonify(data)


@server_manager_blueprint.route('/install-package', methods=['POST'])
async def install_package_route():
    data = await server_management_controller.install_package()
    return jsonify(data)


@server_manager_blueprint.route('/deploy-project', methods=['POST'])
async def deploy_project_route():
    data = await site_management_controller.deploy_project()
    return jsonify(data)


@server_manager_blueprint.route('/create-certbot-cert', methods=['POST'])
async def create_certbot_cert_route():
    data = site_management_controller.create_certbot_cert()
    return jsonify(data)


@server_manager_blueprint.route('/delete-certbot-cert', methods=['DELETE'])
async def delete_certbot_cert_route():
    data = await site_management_controller.delete_certbot_cert()
    return jsonify(data)


@server_manager_blueprint.route('/create-database', methods=['POST'])
async def create_database_route():
    data = await server_management_controller.create_database()
    return jsonify(data)


@server_manager_blueprint.route('/create-database-user', methods=['POST'])
@validate_request({'POST': CreateDatabaseUserSchema})
async def create_database_user_route():
    data = await server_management_controller.create_database_user()
    return jsonify(data)


@server_manager_blueprint.route('/delete-database', methods=['DELETE'])
async def delete_database_route():
    data = await server_management_controller.delete_database()
    return jsonify(data)


@server_manager_blueprint.route('/delete-database-user', methods=['DELETE'])
async def delete_database_user_route():
    data = await server_management_controller.delete_database_user()
    return jsonify(data)


@server_manager_blueprint.route('/update-database-user', methods=['PUT'])
async def update_database_user_route():
    data = await server_management_controller.update_database_user()
    return jsonify(data)


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
