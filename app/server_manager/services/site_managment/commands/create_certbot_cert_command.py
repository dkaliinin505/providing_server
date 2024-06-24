from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class CreateCertBotCertificateCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    def execute(self, data):
        self.config = data

        try:
            self.create_ssl_certificate()
            print(f"SSL certificate created successfully for domain: {self.config.get('domain')}")
        except Exception as e:
            print(f"Failed to create SSL certificate: {str(e)}")

    def create_ssl_certificate(self):
        domain = self.config.get('domain')
        email = self.config.get('email')
        certbot_command = f"sudo certbot --nginx -d {domain} --non-interactive --agree-tos -m {email}"
        run_command(certbot_command)
