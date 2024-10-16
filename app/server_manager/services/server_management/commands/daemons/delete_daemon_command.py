import os
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class DeleteDaemonCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None

    async def execute(self, data):
        self.daemon_id = data.get('daemon_id')

        # Remove daemon config from /etc/supervisord.d
        config_file = f'/etc/supervisord.d/{self.daemon_id}.conf'
        if os.path.exists(config_file):
            await run_command_async(f'sudo rm {config_file}')

        # Reload supervisor to apply changes
        await run_command_async(f'sudo supervisorctl reread && sudo supervisorctl update')

        return {"message": f"Daemon {self.daemon_id} removed."}
