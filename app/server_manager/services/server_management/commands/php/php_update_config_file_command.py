import aiofiles
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class PhpConfigUpdateFileCommand(Command):
    def __init__(self, config):
        self.config = config

    async def write_file_async(self, file_path, content):
        async with aiofiles.open(file_path, mode='w') as file:
            await file.write(content)

    async def execute(self, data):
        php_version = data.get('php_version', '8.1')
        config_content = data.get('config_content', None)
        config_type = data.get('config_type', 'cli')

        if config_type == 'cli':
            # Write new CLI configuration file
            cli_config_path = f'/etc/php/{php_version}/cli/php.ini'
            await self.write_file_async(cli_config_path, config_content)
        else:
            # Fetch the PHP FPM configuration
            fpm_config_path = f'/etc/php/{php_version}/fpm/php.ini'
            await self.write_file_async(fpm_config_path, config_content)

        # Reload PHP FPM service after changes
        await run_command_async(f'sudo service php{php_version}-fpm reload')

        return {
            "message": f"PHP {php_version} configuration updated.",
            "updated_files": bool(config_content)
        }
