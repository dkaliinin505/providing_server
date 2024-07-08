import os
import aiofiles
from pathlib import Path
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command_async, check_file_exists, dir_exists


class NginxCommand(Command):

    def __init__(self, config):
        self.config = config
        self.current_dir = Path(__file__).resolve().parent
        self.template_directory = self.current_dir / '..' / '..' / '..' / 'templates' / 'nginx'

    async def execute(self, data):
        self.config = data.get('config', self.config)

        await run_command_async("sudo apt-get update")

        # Install Nginx
        await run_command_async("sudo apt-get install -y --force-yes nginx")
        await run_command_async("sudo systemctl enable nginx.service")

        # Generate dhparam File
        await run_command_async("sudo openssl dhparam -out /etc/nginx/dhparams.pem 2048")

        # Configure Nginx and PHP-FPM settings
        await self.configure_php_fpm()
        await self.configure_nginx()
        await self.configure_gzip()
        await self.configure_cloudflare()

        # Disable default Nginx site
        if await check_file_exists('/etc/nginx/sites-enabled/default'):
            await run_command_async("sudo rm -f /etc/nginx/sites-enabled/default")
        if await check_file_exists('/etc/nginx/sites-available/default'):
            await run_command_async("sudo rm -f /etc/nginx/sites-available/default")

        await run_command_async("sudo service nginx restart")

        # Install a catch-all server
        await self.install_catch_all_server()

        # Restart Nginx and PHP-FPM services
        await self.restart_services()

        # Add forge user to www-data group
        await run_command_async("sudo usermod -a -G www-data super_forge")
        await run_command_async("sudo id super_forge")
        await run_command_async("sudo groups super_forge")

        # Update logrotate configuration
        file_exists = await run_command_async('sudo test -f /etc/logrotate.d/nginx && echo "exists"')
        if file_exists.strip() == "exists":
            grep_output = await run_command_async('sudo grep --count "maxsize" /etc/logrotate.d/nginx',
                                                  raise_exception=False)
            if grep_output is None or grep_output.strip() == "0":
                await run_command_async(
                    'sudo sed -i "/daily\\|weekly\\|monthly\\|yearly/a maxsize 100M" /etc/logrotate.d/nginx')
        else:
            await run_command_async('echo "daily\nmaxsize 100M\n" | sudo tee /etc/logrotate.d/nginx > /dev/null')

        # Install Node.js and global npm packages
        await self.install_node_js_and_npm_packages()

        return {"message": "Nginx installed and configured successfully"}

    async def configure_php_fpm(self):
        nginx_conf_path = "/etc/nginx/nginx.conf"
        mime_types_path = "/etc/nginx/mime.types"

        if not os.path.exists(nginx_conf_path):
            await self.create_default_nginx_conf(nginx_conf_path)

        if not os.path.exists(mime_types_path):
            await self.create_default_mime_types(mime_types_path)

        memory_limit = self.config.get('memory_limit', '512M')
        if os.path.exists('/etc/php/8.3/fpm/php.ini'):
            await run_command_async(
                f"sudo sed -i 's/memory_limit = .*/memory_limit = {memory_limit}/' /etc/php/8.3/fpm/php.ini")
            await run_command_async(
                "sudo sed -i 's/error_reporting = .*/error_reporting = E_ALL/' /etc/php/8.3/fpm/php.ini")
            await run_command_async(
                "sudo sed -i 's/display_errors = .*/display_errors = Off/' /etc/php/8.3/fpm/php.ini")
            await run_command_async("sudo sed -i 's/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/' /etc/php/8.3/fpm/php.ini")

    async def configure_nginx(self):
        await run_command_async("sudo sed -i 's/user www-data;/user super_forge;/' /etc/nginx/nginx.conf")
        await run_command_async("sudo sed -i 's/worker_processes.*/worker_processes auto;/' /etc/nginx/nginx.conf")
        await run_command_async("sudo sed -i 's/# multi_accept.*/multi_accept on;/' /etc/nginx/nginx.conf")
        await run_command_async(
            "sudo sed -i 's/# server_names_hash_bucket_size.*/server_names_hash_bucket_size 128;/' /etc/nginx/nginx.conf")

    async def create_default_nginx_conf(self, path):
        template_path = (self.template_directory / 'default_nginx_template.conf').resolve()
        async with aiofiles.open(template_path, 'r') as template_file:
            default_conf = await template_file.read()

        await run_command_async(f"echo '{default_conf.strip()}' | sudo tee {path} > /dev/null")

        print(f"Created default Nginx configuration at {path}")

    async def create_default_mime_types(self, path):
        template_path = (self.template_directory / 'mime_types.conf').resolve()
        async with aiofiles.open(template_path, 'r') as template_file:
            mime_types_content = await template_file.read()

        await run_command_async(f"echo '{mime_types_content.strip()}' | sudo tee {path} > /dev/null")

        print(f"Created default mime.types at {path}")

    async def configure_gzip(self):
        template_path = (self.template_directory / 'gzip.conf').resolve()
        async with aiofiles.open(template_path, 'r') as template_file:
            gzip_config = await template_file.read()

        await run_command_async(f"echo '{gzip_config.strip()}' | sudo tee /etc/nginx/conf.d/gzip.conf > /dev/null")

    async def configure_cloudflare(self):
        template_path = (self.template_directory / 'cloudflare.conf').resolve()
        async with aiofiles.open(template_path, 'r') as template_file:
            cloudflare_config = await template_file.read()

        await run_command_async(
            f"echo '{cloudflare_config.strip()}' | sudo tee /etc/nginx/conf.d/cloudflare.conf > /dev/null")

    async def install_catch_all_server(self):
        if not os.path.exists('/etc/nginx/ssl/'):
            await run_command_async("sudo mkdir -p /etc/nginx/ssl/")

        await run_command_async(
            "sudo openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout /etc/nginx/ssl/catch-all.invalid.key -out /etc/nginx/ssl/catch-all.invalid.crt -subj \"/C=US/ST=California/L=San Francisco/O=Example Company/OU=IT/CN=example.com\"")

        template_path = (self.template_directory / 'catch_all_server.conf').resolve()
        async with aiofiles.open(template_path, 'r') as template_file:
            catch_all_config = await template_file.read()

        await run_command_async(
            f"echo '{catch_all_config.strip()}' | sudo tee /etc/nginx/sites-available/000-catch-all > /dev/null")

        if not os.path.exists('/etc/nginx/sites-available/000-catch-all'):
            # Ensure the target file exists before creating the symlink
            await run_command_async("sudo touch /etc/nginx/sites-available/000-catch-all")

        if not os.path.exists('/etc/nginx/sites-enabled/000-catch-all'):
            await run_command_async(
                "sudo ln -s /etc/nginx/sites-available/000-catch-all /etc/nginx/sites-enabled/000-catch-all")

    async def restart_services(self):
        nginx_status = await run_command_async("ps aux | grep nginx | grep -v grep", raise_exception=False)
        if not nginx_status.strip():
            await run_command_async("sudo service nginx start")
            print("Started Nginx")
        else:
            await run_command_async("sudo service nginx reload")
            print("Reloaded Nginx")

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

    async def install_node_js_and_npm_packages(self):
        await run_command_async("sudo apt-get install -y apt-transport-https")
        if not os.path.exists('/etc/apt/keyrings'):
            await run_command_async("sudo mkdir -p /etc/apt/keyrings")

        await run_command_async(
            "sudo curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg")

        node_major = 18

        nodesource_config = f"deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_{node_major}.x nodistro main"
        await run_command_async(
            f"echo '{nodesource_config}' | sudo tee /etc/apt/sources.list.d/nodesource.list > /dev/null")

        await run_command_async("sudo apt-get update")
        await run_command_async("sudo apt-get install -y --force-yes nodejs")

        await run_command_async("sudo npm install -g pm2")
        await run_command_async("sudo npm install -g gulp")
        await run_command_async("sudo npm install -g yarn")
        await run_command_async("sudo npm install -g bun")
