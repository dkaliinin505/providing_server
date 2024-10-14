from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class PhpOpcacheToggleCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        php_version = data.get('php_version', '8.3')
        enable_opcache = data.get('enable_opcache', True)

        # Enable or disable OPCache
        opcache_status = 'On' if enable_opcache else 'Off'
        await run_command_async(
            f'sudo sed -i "s/^opcache.enable=.*/opcache.enable={1 if enable_opcache else 0}/" /etc/php/{php_version}/fpm/php.ini'
        )
        await run_command_async(
            f'sudo sed -i "s/^opcache.enable=.*/opcache.enable={1 if enable_opcache else 0}/" /etc/php/{php_version}/cli/php.ini'
        )

        # Reload PHP FPM after updating OPCache settings
        await run_command_async(f'sudo service php{php_version}-fpm reload')

        return {"message": f"OPCache {'enabled' if enable_opcache else 'disabled'} for PHP {php_version}."}
