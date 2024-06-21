import logging
import os
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command, version_to_int

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CreateSiteCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    def execute(self, data):

        self.config = data
        logging.debug(f"Config: {self.config}")
        self.create_fastcgi_params()
        self.generate_dhparams()
        self.write_nginx_server_block()
        self.add_tls_for_ubuntu()
        self.create_nginx_config_directories()
        self.enable_nginx_sites()
        self.write_redirector()
        self.restart_services()

        return {"message": "Website server configuration created and applied successfully"}

    def create_fastcgi_params(self):
        # Define the path to the templates directory
        template_directory = os.path.join(
            os.path.dirname(__file__),  # Current directory
            '..',  # Move up to the parent directory (commands)
            '..',  # Move up to the parent directory (server_management)
            '..',  # Move up to the parent directory (services)
            'templates',  # Move into the 'templates' directory
            'nginx'  # Move into the 'nginx' directory if needed
        )

        # Define the template file path
        template_path = os.path.join(template_directory, 'fastcgi_params_template.conf')

        # Print the constructed path for verification
        print(f"Template path: {template_path}")

        # Check if the path exists
        if not os.path.isfile(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")

        # Load and use the template
        with open(template_path, 'r') as template_file:
            fastcgi_params = template_file.read()

        run_command(f'echo "{fastcgi_params.strip()}" | sudo tee /etc/nginx/fastcgi_params')

    def generate_dhparams(self):
        if not os.path.isfile('/etc/nginx/dhparams.pem'):
            run_command("sudo openssl dhparam -out /etc/nginx/dhparams.pem 2048")

    def write_nginx_server_block(self):
        domain = self.config.get('domain')
        root_path = self.config.get('root_path', f'/home/super_forge/{domain}/public')

        is_nested_structure = self.config.get('is_nested_structure', False)
        nested_folder = self.config.get('nested_folder', '')

        if is_nested_structure:
            root_path = f'/home/super_forge/{domain}/{nested_folder}/public'

        # Path to the template file
        template_path = os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'nginx', 'nginx_template.conf')

        # Read the template file
        with open(template_path, 'r') as template_file:
            nginx_template = template_file.read()

        # Replace placeholders with actual values
        nginx_config = nginx_template.replace('{{domain}}', domain).replace('{{root_path}}', root_path)

        # Write the config to a temporary file
        with open('/tmp/nginx_server_block.conf', 'w') as f:
            f.write(nginx_config.strip())

        # Move the temporary file to the final location
        run_command(f'sudo mv /tmp/nginx_server_block.conf /etc/nginx/sites-available/{domain}')

    def add_tls_for_ubuntu(self):
        ubuntu_version = run_command("lsb_release -rs").strip()
        domain = self.config.get('domain')
        if version_to_int(ubuntu_version) >= version_to_int("20.04"):
            print(f"Server on Ubuntu {ubuntu_version}")
            config_file_path = f"/etc/nginx/sites-available/{domain}"
            if os.path.exists(config_file_path):
                run_command(f'sudo sed -i "s/ssl_protocols .*/ssl_protocols TLSv1.2 TLSv1.3;/g" {config_file_path}')
            else:
                raise Exception(f"File {config_file_path} does not exist.")

    def create_nginx_config_directories(self):
        run_command(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/before")
        run_command(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/after")
        run_command(f"sudo mkdir -p /etc/nginx/forge-conf/{self.config['domain']}/server")

    def enable_nginx_sites(self):
        run_command(f"sudo rm -f /etc/nginx/sites-enabled/{self.config['domain']}")
        run_command(f"sudo rm -f /etc/nginx/sites-enabled/www.{self.config['domain']}")
        run_command(
            f"sudo ln -s /etc/nginx/sites-available/{self.config['domain']} /etc/nginx/sites-enabled/{self.config['domain']}")

    def write_redirector(self):
        # Path to the template file
        template_path = os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'nginx', 'nginx_redirector_template.conf')

        # Read the template file
        with open(template_path, 'r') as template_file:
            redirector_config = template_file.read()

        # Replace placeholders with actual values
        redirector_config = redirector_config.format(domain=self.config['domain'])

        # Write the content to the /etc/nginx/forge-conf/{domain}/before/redirect.conf file
        with open('/tmp/nginx_redirector.conf', 'w') as f:
            f.write(redirector_config.strip())

        run_command(
            f'sudo mv /tmp/nginx_redirector.conf /etc/nginx/forge-conf/{self.config["domain"]}/before/redirect.conf')

    def restart_services(self):
        run_command("sudo service nginx reload")
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
            if run_command(f"pgrep {version}", raise_exception=False):
                run_command(f"sudo service {version} restart")
