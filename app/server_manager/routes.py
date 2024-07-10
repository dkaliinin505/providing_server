import logging

from quart import Blueprint, jsonify

from __init__ import *

server_manager_blueprint = Blueprint('server_manager', __name__)
task_manager = Controller().task_manager
server_management_controller = ServerManagementController()
site_management_controller = SiteManagementController()


@server_manager_blueprint.route('/generate-deploy-key', methods=['POST'])
@validate_request({'POST': GenerateDeployKeyCommandSchema})
async def generate_deploy_key_route(data):
    result = await server_management_controller.generate_deploy_key(data)
    return jsonify(result)


@server_manager_blueprint.route('/delete-deploy-key', methods=['DELETE'])
@validate_request({'DELETE': GenerateDeployKeyCommandSchema})
async def delete_deploy_key_route(data):
    result = await server_management_controller.delete_deploy_key(data)
    return jsonify(result)


@server_manager_blueprint.route('/create-site', methods=['POST'])
@validate_request({'POST': CreateSiteSchema})
async def create_site_route(data):
    result = await server_management_controller.create_site(data)
    return jsonify(result)


@server_manager_blueprint.route('/install-package', methods=['POST'])
@validate_request({'POST': InstallPackageSchema})
async def install_package_route(data):
    result = await server_management_controller.install_package(data)
    return jsonify(result)


@server_manager_blueprint.route('/deploy-project', methods=['POST'])
@validate_request({'POST': DeployProjectSchema})
async def deploy_project_route(data):
    result = await site_management_controller.deploy_project(data)
    return jsonify(result)


@server_manager_blueprint.route('/create-certbot-cert', methods=['POST'])
@validate_request({'POST': CreateCertBotCertificateSchema})
async def create_certbot_cert_route(data):
    result = site_management_controller.create_certbot_cert(data)
    return jsonify(result)


@server_manager_blueprint.route('/delete-certbot-cert', methods=['DELETE'])
@validate_request({'DELETE': DeleteCertBotCertificateSchema})
async def delete_certbot_cert_route(data):
    result = await site_management_controller.delete_certbot_cert(data)
    return jsonify(result)


@server_manager_blueprint.route('/create-database', methods=['POST'])
@validate_request({'POST': CreateDatabaseSchema})
async def create_database_route(data):
    result = await server_management_controller.create_database(data)
    return jsonify(result)


@server_manager_blueprint.route('/create-database-user', methods=['POST'])
@validate_request({'POST': CreateDatabaseUserSchema})
async def create_database_user_route(data):
    result = await server_management_controller.create_database_user(data)
    return jsonify(result)


@server_manager_blueprint.route('/delete-database', methods=['DELETE'])
@validate_request({'DELETE': DeleteDatabaseSchema})
async def delete_database_route(data):
    result = await server_management_controller.delete_database(data)
    return jsonify(result)


@server_manager_blueprint.route('/delete-database-user', methods=['DELETE'])
@validate_request({'DELETE': DeleteDatabaseUserSchema})
async def delete_database_user_route(data):
    result = await server_management_controller.delete_database_user(data)
    return jsonify(result)


@server_manager_blueprint.route('/update-database-user', methods=['PUT'])
@validate_request({'PUT': CreateDatabaseUserSchema})
async def update_database_user_route(data):
    result = await server_management_controller.update_database_user(data)
    return jsonify(result)


@server_manager_blueprint.route('/test', methods=['GET'])
@validate_request({'GET': RequestSchema})
async def test_route():
    data = await site_management_controller.test()
    logging.info("Returned task id from controller method" + str(data))
    return jsonify(data)


@server_manager_blueprint.route('/task-status/<int:task_id>', methods=['GET'])
async def task_status_route(task_id):
    status = await task_manager.get_task_status(task_id)
    logging.info(f"Status for Task ID {task_id}: {status}")
    return jsonify(status)
