import logging
import re
import shutil
import aiofiles
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command_async

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DeleteCertBotCertCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    async def execute(self, data):
        self.config = data
        await self.remove_ssl_certificate()
        await self.update_nginx_config_for_http()
        return {"message": f"SSL certificate removed successfully for domain: {self.config.get('domain')}"}

    async def remove_ssl_certificate(self):
        domain = self.config['domain']
        await run_command_async(f"sudo certbot delete --cert-name {domain}")

    async def update_nginx_config_for_http(self):
        domain = self.config['domain']
        nginx_config_path = f"/etc/nginx/sites-available/{domain}"
        temp_config_path = f"/tmp/{domain}_nginx_config"

        # Define the regex pattern to find the specific server block
        pattern = re.compile(r"""
                    server\s*{\s*
                    if\s*\(\$host\s*=\s*""" + re.escape(domain) + r"""\)\s*{\s*
                    return\s*301\s*https://\$host\$request_uri;\s*
                    }\s*
                    server_name\s*""" + re.escape(domain) + r""";\s*
                    listen\s*80;\s*
                    return\s*404;\s*
                    }\s*
                    """, re.VERBOSE)

        async with aiofiles.open(nginx_config_path, 'r') as file:
            config_content = await file.read()

        # Remove all SSL-related lines
        config_content = config_content.replace("listen [::]:443 ssl ipv6only=on;", "")
        config_content = config_content.replace("listen 443 ssl;", "")
        config_content = config_content.replace(f"ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;", "")
        config_content = config_content.replace(f"ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;", "")
        config_content = config_content.replace("include /etc/letsencrypt/options-ssl-nginx.conf;", "")
        config_content = config_content.replace("ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;", "")
        config_content = config_content.replace("# managed by Certbot", "")
        config_content = re.sub(pattern, '', config_content)

        async with aiofiles.open(temp_config_path, 'w') as file:
            await file.write(config_content)

        shutil.move(temp_config_path, nginx_config_path)
        await run_command_async("sudo systemctl restart nginx")
