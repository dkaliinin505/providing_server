from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class PhpVersionInstallCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        # Get PHP version, default to 8.1 if not provided
        php_version = data.get('php_version', '8.1')

        # Get the CLI and Sites default versions (optional, default to 8.1)
        cli_default_version = data.get('cli_default_version', '8.1')
        sites_default_version = data.get('sites_default_version', '8.1')

        # Install the PHP version and common extensions
        await run_command_async(f"sudo apt-get install -y php{php_version}-fpm php{php_version}-cli")
        await run_command_async(
            f"sudo apt-get install -y php{php_version}-common php{php_version}-curl php{php_version}-mbstring php{php_version}-xml")

        # Update PHP CLI to point to the CLI default version
        await run_command_async(f"sudo update-alternatives --set php /usr/bin/php{cli_default_version}")

        # Optionally set the default version for Sites if needed
        # Assuming this is managed via FPM or Nginx configuration
        await run_command_async(f"sudo update-alternatives --set php-fpm /usr/sbin/php-fpm{sites_default_version}")

        return {
            "message": f"PHP {php_version} installed and configured. CLI default version set to {cli_default_version}, "
                       f"Sites default version set to {sites_default_version}."
        }
