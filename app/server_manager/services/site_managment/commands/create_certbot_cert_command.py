import asyncio
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command_async


class CreateCertBotCertificateCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    async def execute(self, data):
        self.config = data
        await self.check_and_install_certbot()
        try:
            await self.create_ssl_certificate()
            await run_command_async("sudo systemctl restart nginx")
            return {"message": f"SSL certificate created successfully for domain: {self.config.get('domain')}"}
        except Exception as e:
            return {f"Failed to create SSL certificate: {str(e)}"}

    async def create_ssl_certificate(self):
        domain = self.config.get('domain')
        email = self.config.get('email')
        certbot_command = f"sudo certbot --nginx -d {domain} --non-interactive --agree-tos -m {email}"
        await run_command_async(certbot_command)

    async def check_and_install_certbot(self):
        try:
            await run_command_async("certbot --version")
        except Exception:
            print("Certbot not found. Installing...")
            await run_command_async("sudo apt update")
            await run_command_async("sudo apt install -y certbot python3-certbot-nginx")
