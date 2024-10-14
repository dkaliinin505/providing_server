import aiofiles
import tempfile
import os
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class PhpConfigUpdateFileCommand(Command):
    def __init__(self, config):
        self.config = config

    async def write_temp_file_async(self, content):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        async with aiofiles.open(temp_file.name, mode='w') as file:
            await file.write(content)
        return temp_file.name

    async def execute(self, data):
        php_version = data.get('php_version', '8.1')
        config_content = data.get('content', None)
        config_type = data.get('type', 'cli')

        if config_type == 'cli':
            cli_config_path = f'/etc/php/{php_version}/cli/php.ini'
        else:
            fpm_config_path = f'/etc/php/{php_version}/fpm/php.ini'

        config_path = cli_config_path if config_type == 'cli' else fpm_config_path

        temp_file_path = await self.write_temp_file_async(config_content)

        await run_command_async(f'sudo mv {temp_file_path} {config_path}')

        await run_command_async(f'sudo service php{php_version}-fpm reload')

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return {
            "message": f"PHP {php_version} configuration updated.",
            "updated_files": bool(config_content)
        }
