import logging
from pathlib import Path
import aiofiles
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command_async, version_to_int, check_file_exists

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CreateSiteCommand(Command):
    def __init__(self, config):
        self.config = config
        self.current_dir = Path(__file__).resolve().parent
        print(f"Config: {config}")

    async def execute(self, data):
        from app import app_instance
        self.config = data
        logging.debug(f"Config in CreateSiteCommand : {self.config}")

        async with app_instance.app.app_context():
            await self.create_fastcgi_params()
            await self.generate_dhparams()
            await self.write_nginx_server_block()
            await self.add_tls_for_ubuntu()
            await self.create_nginx_config_directories()
            await self.enable_nginx_sites()
            await self.write_redirector()
            await self.restart_services()

        return {"message": "Website server configuration created and applied successfully"}

    async def create_fastcgi_params(self):
        template_directory = Path(__file__).resolve().parent / '..' / '..' / '..' / 'templates' / 'nginx'
        template_path = template_directory / 'fastcgi_params_template.conf'

        async with aiofiles.open(template_path, 'r') as template_file:
            fastcgi_params = await template_file.read()

        async with aiofiles.open('/tmp/fastcgi_params', 'w') as temp_file:
            await temp_file.write(fastcgi_params)

        await run_command_async('sudo mv /tmp/fastcgi_params /etc/nginx/fastcgi_params')
        logging.debug("FastCGI params created")

    async def generate_dhparams(self):
        if not await check_file_exists('/etc/nginx/dhparams.pem'):
            await run_command_async("sudo openssl dhparam -out /etc/nginx/dhparams.pem 2048")

    async def write_nginx_server_block(self):
        domain = self.config.get('domain')
        root_path = self.config.get('root_path', f'/home/super_forge/{domain}/public')

        is_nested_structure = self.config.get('is_nested_structure', False)
        nested_folder = self.config.get('nested_folder', '')

        if is_nested_structure:
            root_path = f'/home/super_forge/{domain}/{nested_folder}/public'

        template_directory = self.current_dir / '..' / '..' / '..' / 'templates' / 'nginx'
        template_path = (template_directory / 'nginx_template.conf').resolve()

        async with aiofiles.open(template_path, 'r') as template_file:
            nginx_template = await template_file.read()

        nginx_config = nginx_template.replace('{{domain}}', domain).replace('{{root_path}}', root_path)

        async with aiofiles.open('/tmp/nginx_server_block.conf', 'w') as f:
            await f.write(nginx_config)

        await run_command_async(f'sudo mv /tmp/nginx_server_block.conf /etc/nginx/sites-available/{domain}')
        logging.debug("Nginx server block written")

    async def add_tls_for_ubuntu(self):
        ubuntu_version = await run_command_async("lsb_release -rs")
        ubuntu_version = ubuntu_version.strip()
        domain = self.config.get('domain')
        if version_to_int(ubuntu_version) >= version_to_int("20.04"):
            print(f"Server on Ubuntu {ubuntu_version}")
            config_file_path = f"/etc/nginx/sites-available/{domain}"
            if await check_file_exists(config_file_path):
                await run_command_async(
                    f'sudo sed -i "s/ssl_protocols .*/ssl_protocols TLSv1.2 TLSv1.3;/g" {config_file_path}')
            else:
                raise Exception(f"File {config_file_path} does not exist.")
        logging.debug("TLS added for Ubuntu")

    async def create_nginx_config_directories(self):
        await run_command_async(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/before")
        await run_command_async(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/after")
        await run_command_async(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/server")
        logging.debug("Nginx config directories created")

    async def enable_nginx_sites(self):
        await run_command_async(f"sudo rm -f /etc/nginx/sites-enabled/{self.config['domain']}")
        await run_command_async(f"sudo rm -f /etc/nginx/sites-enabled/www.{self.config['domain']}")
        await run_command_async(
            f"sudo ln -s /etc/nginx/sites-available/{self.config['domain']} /etc/nginx/sites-enabled/{self.config['domain']}")
        logging.debug("Nginx sites enabled")

    async def write_redirector(self):
        domain = self.config['domain']
        template_directory = self.current_dir / '..' / '..' / '..' / 'templates' / 'nginx'
        template_path = (template_directory / 'nginx_redirector_template.conf').resolve()

        if not await check_file_exists(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        async with aiofiles.open(template_path, 'r') as template_file:
            redirector_config = await template_file.read()

        redirector_config = redirector_config.replace('{domain}', domain)

        async with aiofiles.open('/tmp/nginx_redirector.conf', 'w') as f:
            await f.write(redirector_config)

        await run_command_async(
            f'sudo mv /tmp/nginx_redirector.conf /etc/nginx/forge-conf/{self.config["domain"]}/before/redirect.conf')
        logging.debug("Redirector written")

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
