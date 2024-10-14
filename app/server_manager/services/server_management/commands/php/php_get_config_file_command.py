from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, read_file_async


class PhpGetConfigFileCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        php_version = data.get('php_version', '8.1')
        php_type = data.get('type', 'cli')

        if php_type == 'cli':
            # Fetch the PHP CLI configuration
            cli_config_path = f"/etc/php/{php_version}/cli/php.ini"
            content = await read_file_async(cli_config_path)
        else:
            # Fetch the PHP FPM configuration
            fpm_config_path = f"/etc/php/{php_version}/fpm/php.ini"
            content = await read_file_async(fpm_config_path)

        return {
            "message": f"PHP {php_version} configuration fetched.",
            "data": content
        }
