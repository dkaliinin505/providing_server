from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class PhpVersionInstallCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        php_version = data.get('php_version', '8.1')
        await run_command_async(f"sudo apt-get install -y php{php_version}-fpm php{php_version}-cli")

        # Optionally install additional extensions based on the version
        await run_command_async(
            f"sudo apt-get install -y php{php_version}-common php{php_version}-curl php{php_version}-mbstring php{php_version}-xml")

        # Update PHP CLI to point to the newly installed version
        await run_command_async(f"sudo update-alternatives --set php /usr/bin/php{php_version}")

        return {"message": f"PHP {php_version} installed and configured."}
