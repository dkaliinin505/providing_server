from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class PhpConfigUpdateCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        php_version = data.get('php_version', '8.3')
        config_updates = data.get('config_updates', {})

        # Update PHP configuration settings
        for setting, value in config_updates.items():
            await run_command_async(
                f'sudo sed -i "s/^{setting} = .*/{setting} = {value}/" /etc/php/{php_version}/fpm/php.ini'
            )
            await run_command_async(
                f'sudo sed -i "s/^{setting} = .*/{setting} = {value}/" /etc/php/{php_version}/cli/php.ini'
            )

        # Reload PHP FPM after updating configuration
        await run_command_async(f'sudo service php{php_version}-fpm reload')

        return {"message": f"PHP {php_version} configuration updated."}
