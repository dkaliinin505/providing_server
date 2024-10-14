import logging

from quart import Blueprint, jsonify

from .imports import *

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


@server_manager_blueprint.route('/delete-site', methods=['DELETE'])
@validate_request({'DELETE': DeleteSiteSchema})
async def delete_site_route(data):
    result = await server_management_controller.delete_site(data)
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
    result = await site_management_controller.create_certbot_cert(data)
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
async def test_route(data):
    result = await site_management_controller.test(data)
    logging.info("Returned task id from controller method" + str(result))
    return jsonify(result)


@server_manager_blueprint.route('/create-queue-worker', methods=['POST'])
@validate_request({'POST': CreateQueueWorkerSchema})
async def create_queue_worker_route(data):
    result = await site_management_controller.create_queue_worker(data)
    return jsonify(result)


@server_manager_blueprint.route('/delete-queue-worker', methods=['DELETE'])
@validate_request({'DELETE': DeleteQueueWorkerSchema})
async def delete_queue_worker_route(data):
    result = await site_management_controller.delete_queue_worker(data)
    return jsonify(result)


@server_manager_blueprint.route('/restart-queue-worker', methods=['POST'])
@validate_request({'POST': RestartQueueWorkerSchema})
async def restart_queue_worker_route(data):
    result = await site_management_controller.restart_queue_worker(data)
    return jsonify(result)


@server_manager_blueprint.route('/get-queue-worker-logs', methods=['GET'])
@validate_request({'GET': GetQueueWorkerLogsSchema})
async def get_queue_worker_logs_route(data):
    result = await site_management_controller.get_queue_worker_logs(data)
    return jsonify(result)


@server_manager_blueprint.route('/get-queue-worker-info', methods=['GET'])
@validate_request({'GET': GetQueueWorkerInfoSchema})
async def get_queue_worker_info_route(data):
    result = await site_management_controller.get_queue_worker_info(data)
    return jsonify(result)


@server_manager_blueprint.route('/get-workers-status', methods=['GET'])
@validate_request({'GET': RequestSchema})
async def get_workers_status_route(data):
    result = await site_management_controller.get_workers_status(data)
    return jsonify(result)


@server_manager_blueprint.route('/pull-project', methods=['POST'])
@validate_request({'POST': PullProjectSchema})
async def pull_project_route(data):
    result = await site_management_controller.pull_project(data)
    return jsonify(result)


@server_manager_blueprint.route('/php-version-install', methods=['POST'])
@validate_request({'POST': PhpVersionInstallSchema})
async def php_version_install_route(data):
    result = await server_management_controller.php_version_install(data)
    return jsonify(result)


@server_manager_blueprint.route('/php-config-update', methods=['PUT'])
@validate_request({'PUT': PhpConfigUpdateSchema})
async def php_config_update_route(data):
    result = await server_management_controller.php_config_update(data)
    return jsonify(result)


@server_manager_blueprint.route('/php-toggle-opcache', methods=['PUT'])
@validate_request({'PUT': PhpToggleOpcacheSchema})
async def php_toggle_opcache_route(data):
    result = await server_management_controller.php_toggle_opcache(data)
    return jsonify(result)


@server_manager_blueprint.route('/php-update-config-file', methods=['PUT'])
@validate_request({'PUT': PhpUpdateConfigFileSchema})
async def php_update_config_file_route(data):
    result = await server_management_controller.php_update_config_file(data)
    return jsonify(result)


@server_manager_blueprint.route('/php-get-config-file', methods=['POST'])
@validate_request({'POST': PhpGetConfigFileSchema})
async def php_get_config_file_route(data):
    result = await server_management_controller.php_get_config_file(data)
    return jsonify(result)


@server_manager_blueprint.route('/task-status/<task_id>', methods=['GET'])
async def task_status_route(task_id):
    status = await task_manager.get_task_status(task_id)
    logging.info(f"Status for Task ID {task_id}: {status}")
    status_code = 500
    match status.get("status"):
        case "completed":
            status_code = 200
        case "in_progress":
            status_code = 202
        case "error":
            status_code = 400

    return jsonify(status), status_code
