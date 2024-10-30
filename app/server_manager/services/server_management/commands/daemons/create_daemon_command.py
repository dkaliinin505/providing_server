import aiofiles
import logging
from pathlib import Path
import uuid

from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CreateDaemonCommand(Command):
    def __init__(self, config):
        self.daemon_id = None
        self.config = config

    async def execute(self, data):
        self.config = data
        self.daemon_id = str(uuid.uuid4())
        await self.create_supervisor_conf()
        await self.update_supervisor()
        await self.start_daemon()

        return {"message": f"Daemon {self.daemon_id} started successfully.", "data": self.daemon_id}

    async def create_supervisor_conf(self):
        daemon_id = self.daemon_id
        command = self.config.get('command')
        directory = self.config.get('directory', '/')
        user = self.config.get('user', 'root')
        num_processes = self.config.get('num_processes', 1)
        start_seconds = self.config.get('start_seconds', 1)
        stop_seconds = self.config.get('stop_seconds', 5)
        stop_signal = self.config.get('stop_signal', 'SIGTERM')
        log_dir = Path(f"/home/{user}/.logs")
        supervisor_conf_dir = Path("/etc/supervisor/conf.d")

        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Log directory created at {log_dir}")

        conf_content = f"""
        [program:{daemon_id}]
        command={command}
        directory={directory}
        user={user}
        numprocs={num_processes}
        startsecs={start_seconds}
        stopwaitsecs={stop_seconds}
        stopsignal={stop_signal}
        stdout_logfile={log_dir}/daemon-{daemon_id}.log
        stdout_logfile_maxbytes=5MB
        stdout_logfile_backups=3
        autostart=true
        autorestart=true
        """

        if num_processes == 1:
            conf_content += "process_name=%(program_name)s\n"
        elif num_processes > 1:
            conf_content += "process_name=%(program_name)s_%(process_num)s\n"

        conf_path = supervisor_conf_dir / f"{daemon_id}.conf"

        async with aiofiles.open('/tmp/supervisor_daemon.conf', 'w') as temp_file:
            await temp_file.write(conf_content)

        await run_command_async(f'sudo mv /tmp/supervisor_daemon.conf {conf_path}')
        logging.debug(f"Supervisor config for daemon {daemon_id} created at {conf_path}.")

    async def update_supervisor(self):
        await run_command_async("sudo supervisorctl reread")
        await run_command_async("sudo supervisorctl update")
        logging.debug("Supervisor configuration updated.")

    async def start_daemon(self):
        daemon_id = self.daemon_id
        await run_command_async(f"sudo supervisorctl start {daemon_id}")
        logging.debug(f"Daemon {daemon_id} started.")
