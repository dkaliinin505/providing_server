import os

import aiofiles

from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class UpdateDaemonCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None
        self.command = None
        self.directory = None
        self.user = None
        self.num_processes = None
        self.start_seconds = None
        self.stop_seconds = None
        self.stop_signal = None

    async def execute(self, data):
        self.daemon_id = data.get('daemon_id')
        self.command = data.get('command')
        self.directory = data.get('directory', '/')
        self.user = data.get('user', 'root')
        self.num_processes = data.get('num_processes', 1)
        self.start_seconds = data.get('start_seconds', 1)
        self.stop_seconds = data.get('stop_seconds', 5)
        self.stop_signal = data.get('stop_signal', 'TERM')

        # Create user-writable config path
        user_config_dir = f"/home/{self.user}/daemon_configs"
        os.makedirs(user_config_dir, exist_ok=True)

        daemon_config = f"""
        [program:{self.daemon_id}]
        command={self.command}
        directory={self.directory}
        user={self.user}
        numprocs={self.num_processes}
        startsecs={self.start_seconds}
        stopwaitsecs={self.stop_seconds}
        stopsignal={self.stop_signal}
        """

        # Write the daemon config file to user directory
        user_config_file = f"{user_config_dir}/{self.daemon_id}.conf"
        async with aiofiles.open(user_config_file, 'w') as f:
            await f.write(daemon_config)

        # Move the config to /etc/supervisord.d/ with sudo privileges
        await run_command_async(f'sudo mv {user_config_file} /etc/supervisord.d/{self.daemon_id}.conf')

        # Reload supervisor to apply changes
        await run_command_async(f'sudo supervisorctl reread && sudo supervisorctl update')

        return {"message": f"Daemon {self.daemon_id} updated successfully.", "data": self.daemon_id}
