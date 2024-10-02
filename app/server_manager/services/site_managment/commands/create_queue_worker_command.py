import aiofiles
import logging
from pathlib import Path

from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CreateQueueWorkerCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config = data
        await self.check_artisan_exists()
        await self.create_supervisor_conf()
        await self.update_supervisor()
        await self.start_worker()

        return {"message": f"Worker {self.config.get('worker_id')} started successfully."}

    async def check_artisan_exists(self):
        artisan_path = self.config.get('artisan_path')
        if not await check_file_exists(artisan_path):
            return {f"Could not locate Laravel's 'artisan' script at {artisan_path}."}
        logging.debug(f"Artisan script found at {artisan_path}")

    async def create_supervisor_conf(self):
        worker_id = self.config.get('worker_id')
        artisan_path = self.config.get('artisan_path')
        user = self.config.get('user', 'super_forge')
        queue = self.config.get('queue', 'default')
        sleep = self.config.get('sleep', 10)
        timeout = self.config.get('timeout', 60)
        delay = self.config.get('delay', 10)
        memory = self.config.get('memory', 256)
        tries = self.config.get('tries', 1)
        log_dir = Path(f"/home/{user}/.logs")
        supervisor_conf_dir = Path("/etc/supervisor/conf.d")

        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
            logging.debug(f"Log directory created at {log_dir}")

        conf_content = f"""
        [program:worker-{worker_id}]
        command=php8.3 {artisan_path} queue:work database --sleep={sleep} --daemon --quiet --timeout={timeout} --delay={delay} --memory={memory} --tries={tries} --force --queue="{queue}"

        process_name=%(program_name)s_%(process_num)02d
        autostart=true
        autorestart=true
        stopasgroup=true
        killasgroup=true
        user={user}
        numprocs=1
        stopwaitsecs=10
        stdout_logfile={log_dir}/worker-{worker_id}.log
        stdout_logfile_maxbytes=5MB
        stdout_logfile_backups=3
        """

        conf_path = supervisor_conf_dir / f"worker-{worker_id}.conf"

        async with aiofiles.open('/tmp/supervisor_worker.conf', 'w') as temp_file:
            await temp_file.write(conf_content)

        await run_command_async(f'sudo mv /tmp/supervisor_worker.conf {conf_path}')
        logging.debug(f"Supervisor config for worker {worker_id} created.")

    async def update_supervisor(self):
        await run_command_async("sudo supervisorctl reread")
        await run_command_async("sudo supervisorctl update")
        logging.debug("Supervisor configuration updated.")

    async def start_worker(self):
        worker_id = self.config.get('worker_id')
        await run_command_async(f"sudo supervisorctl start worker-{worker_id}:*")
        logging.debug(f"Worker {worker_id} started.")