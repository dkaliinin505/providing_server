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
        #self.remove_ssl_certificate()
        self.update_nginx_config_for_http()
        print(f"SSL certificate removed successfully for domain: {self.config.get('domain')}")

    def remove_ssl_certificate(self):
        domain = self.config['domain']
        run_command(f"sudo certbot delete --cert-name {domain}")

    def update_nginx_config_for_http(self):
        domain = self.config['domain']
        nginx_config_path = f"/etc/nginx/sites-available/{domain}"
        temp_config_path = f"/tmp/{domain}_nginx_config"

        with open(nginx_config_path, 'r') as file:
            config_content = file.readlines()

        modified_content = []
        inside_redirect_block = False
        inside_server_block = False
        brace_count = 0
        redirect_block_lines = []

        for line in config_content:
            if "listen [::]:443 ssl ipv6only=on;" in line or "listen 443 ssl;" in line or \
                    f"ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;" in line or \
                    f"ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;" in line or \
                    "include /etc/letsencrypt/options-ssl-nginx.conf;" in line or "ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;" in line or \
                    " managed by Certbot" in line:
                continue

            if re.search(r'server\s*{', line) and re.search(
                    r'if\s*\(\$host\s*=\s*{}\)\s*{{\s*return\s*301\s*https://\$host\$request_uri;'.format(
                        domain.replace('.', '\.')), line):
                inside_redirect_block = True
                brace_count = 1
                redirect_block_lines.append(line)
                continue

            if inside_redirect_block:
                brace_count += line.count('{') - line.count('}')
                redirect_block_lines.append(line)
                if brace_count == 0:
                    inside_redirect_block = False
                    continue

            modified_content.append(line)

        if redirect_block_lines:
            modified_content = [
                line for line in modified_content
                if line not in redirect_block_lines
            ]

        # Print the number of substitutions made
        logging.info(f"Number of lines in config: {len(config_content)}")

        # Print config content after modification
        logging.info("Modified Nginx Config Content:\n", "".join(modified_content))

        with open(temp_config_path, 'w') as file:
            file.writelines(modified_content)

        shutil.move(temp_config_path, nginx_config_path)
        run_command("sudo systemctl reload nginx")
