import os
import aiofiles
from pathlib import Path

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
        self.stop_signal = data.get('stop_signal', 'SIGTERM')

        log_dir = Path(f"/home/{self.user}/.logs")
        supervisor_conf_dir = Path("/etc/supervisor/conf.d")

        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)

        daemon_config = f"""
        [program:{self.daemon_id}]
        command={self.command}
        directory={self.directory}
        user={self.user}
        numprocs={self.num_processes}
        startsecs={self.start_seconds}
        stopwaitsecs={self.stop_seconds}
        stopsignal={self.stop_signal}
        stdout_logfile={log_dir}/daemon-{self.daemon_id}.log
        stdout_logfile_maxbytes=5MB
        stdout_logfile_backups=3
        autostart=true
        autorestart=true
        """

        if self.num_processes == 1:
            daemon_config += "process_name=%(program_name)s\n"
        else:
            daemon_config += "process_name=%(program_name)s_%(process_num)s\n"

        async with aiofiles.open('/tmp/supervisor_daemon_update.conf', 'w') as temp_file:
            await temp_file.write(daemon_config)

        conf_path = supervisor_conf_dir / f"{self.daemon_id}.conf"
        await run_command_async(f'sudo mv /tmp/supervisor_daemon_update.conf {conf_path}')

        await run_command_async("sudo supervisorctl reread")
        await run_command_async("sudo supervisorctl update")

        return {"message": f"Daemon updated successfully.", "data": self.daemon_id}
