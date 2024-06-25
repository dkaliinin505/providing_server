import logging
import re
import shutil

from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class DeleteCertBotCertCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    def execute(self, data):
        self.config = data
        self.remove_ssl_certificate()
        self.update_nginx_config_for_http()
        return {"message": f"SSL certificate removed successfully for domain: {self.config.get('domain')}"}

    def remove_ssl_certificate(self):
        domain = self.config['domain']
        run_command(f"sudo certbot delete --cert-name {domain}")

    def update_nginx_config_for_http(self):
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

        with open(nginx_config_path, 'r') as file:
            config_content = file.read()

        # Remove all SSL-related lines
        config_content = config_content.replace("listen [::]:443 ssl ipv6only=on;", "")
        config_content = config_content.replace("listen 443 ssl;", "")
        config_content = config_content.replace(f"ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;",
                                                "")
        config_content = config_content.replace(f"ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;",
                                                "")
        config_content = config_content.replace("include /etc/letsencrypt/options-ssl-nginx.conf;", "")
        config_content = config_content.replace("ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;", "")
        config_content = config_content.replace("# managed by Certbot", "")
        config_content = re.sub(pattern, '', config_content)

        with open(temp_config_path, 'w') as file:
            file.write(config_content)

        shutil.move(temp_config_path, nginx_config_path)
        run_command("sudo systemctl restart nginx")
