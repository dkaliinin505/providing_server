import logging
import shutil
from pathlib import Path
import aiofiles
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists, dir_exists

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DeleteSiteCommand(Command):
    def __init__(self, config):
        self.config = config
        self.current_dir = Path(__file__).resolve().parent

    async def execute(self, data):
        self.config = data
        logging.debug(f"Config in DeleteSiteCommand : {self.config}")

        await self.disable_nginx_site()
        await self.remove_nginx_config_files()
        await self.remove_nginx_config_directories()
        await self.restart_services()
        await self.remove_directory(f"/home/super_forge/{self.config['domain']}")

        return {"message": "Website server configuration removed successfully"}

    async def disable_nginx_site(self):
        domain = self.config['domain']
        await run_command_async(f"sudo rm -f /etc/nginx/sites-enabled/{domain}")
        await run_command_async(f"sudo rm -f /etc/nginx/sites-enabled/www.{domain}")
        logging.debug("Nginx sites disabled")

    async def remove_nginx_config_files(self):
        domain = self.config['domain']
        config_file_path = f"/etc/nginx/sites-available/{domain}"
        if await check_file_exists(config_file_path):
            await run_command_async(f"sudo rm -f {config_file_path}")
            logging.debug(f"Nginx config file {config_file_path} removed")
        else:
            logging.warning(f"Nginx config file {config_file_path} does not exist")

        redirector_config_path = f"/etc/nginx/forge-conf/{domain}/before/redirect.conf"
        if await check_file_exists(redirector_config_path):
            await run_command_async(f"sudo rm -f {redirector_config_path}")
            logging.debug(f"Nginx redirector config file {redirector_config_path} removed")
        else:
            logging.warning(f"Nginx redirector config file {redirector_config_path} does not exist")

    async def remove_nginx_config_directories(self):
        domain = self.config['domain']
        await run_command_async(f"sudo rm -rf /etc/nginx/forge-conf/{domain}")
        logging.debug(f"Nginx config directories for {domain} removed")

    async def remove_directory(self, directory):
        if await dir_exists(directory):
            shutil.rmtree(directory)
            logging.debug(f"Directory {directory} removed")
        else:
            logging.warning(f"Directory {directory} does not exist")

    async def restart_services(self):
        await run_command_async("sudo service nginx reload")
        php_fpm_versions = [
            "php8.3-fpm",
            "php8.2-fpm",
            "php8.1-fpm",
            "php8.0-fpm",
            "php7.4-fpm",
            "php7.3-fpm",
            "php7.2-fpm",
            "php7.1-fpm",
            "php7.0-fpm",
            "php5.6-fpm",
            "php5-fpm"
        ]

        for version in php_fpm_versions:
            if await run_command_async(f"pgrep {version}", raise_exception=False):
                await run_command_async(f"sudo service {version} restart")
        logging.debug("Services restarted")
