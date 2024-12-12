import logging

from quart import jsonify

from app.server_manager.controllers.controller import Controller
from app.server_manager.services.package_installer.package_installer_service import PackageInstallerService
from app.server_manager.services.server_management.server_management_service import ServerManagementService


class ServerManagementController(Controller):
    def __init__(self):
        super().__init__()
        self.server_management_service = ServerManagementService()
        self.package_installer_service = PackageInstallerService()

    async def generate_deploy_key(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.generate_deploy_key, data)
        logging.info(
            f"Generate Deploy Key Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Generate Deploy Key Task started in background", "task_id": task_id}

    async def delete_deploy_key(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_deploy_key, data)
        logging.info(
            f"Delete Deploy Key Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Delete Deploy Key Task started in background", "task_id": task_id}

    async def create_site(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.create_site, data)
        logging.info(f"Create Site Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Create Site Task started in background", "task_id": task_id}

    async def delete_site(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_site, data)
        logging.info(f"Delete Site Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Delete Site Task started in background", "task_id": task_id}

    async def install_package(self, data):
        task_id = await self.task_manager.submit_task(self.package_installer_service.install_package, data)
        logging.info(
            f"Install Package Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Install Package Task started in background", "task_id": task_id}

    async def create_database(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.create_database, data)
        logging.info(
            f"Create Database Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Create database started in background", "task_id": task_id}

    async def create_database_user(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.create_database_user, data)
        logging.info(
            f"Create Database User Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Create database User task started in background", "task_id": task_id}

    async def delete_database(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_database, data)
        logging.info(
            f"Delete Database Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Database delete task started in background", "task_id": task_id}

    async def delete_database_user(self, data):
        logging.info(f"Delete Database User Task in ServerManagementController started with data: {data}")
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_database_user, data)
        logging.info(
            f"Delete Database User Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Delete database user task started in background", "task_id": task_id}

    async def update_database_user(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.update_database_user, data)
        logging.info(
            f"Update Database User Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Updated database user task started in background", "task_id": task_id}

    async def php_version_install(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.php_version_install, data)
        logging.info(
            f"PHP Version Install Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "PHP Version Install task started in background", "task_id": task_id}

    async def php_config_update(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.php_config_update, data)
        logging.info(
            f"PHP Config Update Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "PHP Config Update task started in background", "task_id": task_id}

    async def php_toggle_opcache(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.php_toggle_opcache, data)
        logging.info(
            f"PHP Toggle Opcache Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "PHP Toggle Opcache task started in background", "task_id": task_id}

    async def php_update_config_file(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.php_update_config_file, data)
        logging.info(
            f"PHP Update Config File Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "PHP Update Config File task started in background", "task_id": task_id}

    async def php_get_config_file(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.php_get_config_file, data)
        logging.info(
            f"PHP Get Config File Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "PHP Get Config File task started in background", "task_id": task_id}

    async def php_version_delete(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.php_version_delete, data)
        logging.info(
            f"PHP Version Delete Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "PHP Version Delete task started in background", "task_id": task_id}

    async def create_scheduler_job(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.create_scheduled_job, data)
        logging.info(
            f"Create Scheduler Job Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Create Scheduler Job task started in background", "task_id": task_id}

    async def update_scheduler_job(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.update_scheduled_job, data)
        logging.info(
            f"Update Scheduler Job Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Update Scheduler Job task started in background", "task_id": task_id}

    async def delete_scheduler_job(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_scheduled_job, data)
        logging.info(
            f"Delete Scheduler Job Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Delete Scheduler Job task started in background", "task_id": task_id}

    async def get_scheduler_job_logs(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.get_scheduler_job_logs, data)
        logging.info(
            f"Get Scheduler Job Logs Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Get Scheduler Job Logs task started in background", "task_id": task_id}

    async def run_scheduler_job(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.run_scheduled_job, data)
        logging.info(
            f"Run Scheduler Job Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Run Scheduler Job task started in background", "task_id": task_id}

    async def control_scheduler_job(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.control_scheduled_job, data)
        logging.info(
            f"Control Scheduler Job Task in ServerManagementController started in background with task_id: {task_id}")
        return {"message": "Control Scheduler Job task started in background", "task_id": task_id}

    async def delete_daemon(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_daemon, data)
        return {"message": "Delete Daemon Task started in background", "task_id": task_id}

    async def update_daemon(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.update_daemon, data)
        return {"message": "Update Daemon Task started in background", "task_id": task_id}

    async def create_daemon(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.create_daemon, data)
        return {"message": "Create Daemon Task started in background", "task_id": task_id}

    async def control_daemon(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.control_daemon, data)
        return {"message": "Control Daemon Task started in background", "task_id": task_id}

    async def get_daemon_status(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.get_daemon_status, data)
        return {"message": "Get Daemon Status Task started in background", "task_id": task_id}

    async def get_daemon_logs(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.get_daemon_logs, data)
        return {"message": "Get Daemon Logs Task started in background", "task_id": task_id}

    async def clear_daemon_logs(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.clear_daemon_logs, data)
        return {"message": "Clear Daemon Logs Task started in background", "task_id": task_id}

    async def add_firewall_rule(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.add_firewall_rule, data)
        return {"message": "Add Firewall Rule Task started in background", "task_id": task_id}

    async def remove_firewall_rule(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.remove_firewall_rule, data)
        return {"message": "Remove Firewall Rule Task started in background", "task_id": task_id}

    async def get_server_logs(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.get_server_logs, data)
        return {"message": "Get Server Logs Task started in background", "task_id": task_id}

    async def clear_server_logs(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.clear_server_logs, data)
        return {"message": "Clear Server Logs Task started in background", "task_id": task_id}

    async def add_ssh_key(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.add_ssh_key, data)
        return {"message": "Add SSH Key Task started in background", "task_id": task_id}

    async def remove_ssh_key(self, data):
        task_id = await self.task_manager.submit_task(self.server_management_service.delete_ssh_key, data)
        return {"message": "Remove SSH Key Task started in background", "task_id": task_id}

    def __del__(self):
        super().cleanup(resource_types=[ServerManagementService, PackageInstallerService])

