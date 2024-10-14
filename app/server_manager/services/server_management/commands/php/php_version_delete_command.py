from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class PhpVersionDeleteCommand(Command):
    def __init__(self, config):
        self.config = config

    async def is_default_version(self):
        php_version = self.config.get('php_version', '8.1')
        default_version = await run_command_async('php -r "echo PHP_VERSION;"')

        return default_version.startswith(php_version)

    async def count_installed_php_versions(self):
        result = await run_command_async("ls /etc/php/ | wc -l")

        return int(result.strip())

    async def execute(self, data):
        if await self.is_default_version():
            return {"error": "You cannot delete the default PHP version."}

        await run_command_async(f"sudo apt-get purge php{self.config.get('php_version', '8.1')}* -y")
        return {"message": f"PHP {self.config.get('php_version', '8.1')} successfully deleted."}
