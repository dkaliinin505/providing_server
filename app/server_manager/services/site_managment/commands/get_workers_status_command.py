import logging
import asyncio

from app.server_manager.interfaces.command_interface import Command

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GetSupervisorStatusCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        return await self.get_worker_status()

    async def get_worker_status(self):
        try:
            process = await asyncio.create_subprocess_exec(
                'sudo', 'supervisorctl', 'status',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logging.error(f"Failed to execute supervisorctl status: {stderr.decode()}")
                return {"error": "Failed to get supervisor status", "details": stderr.decode()}

            workers = self.parse_status_output(stdout.decode())
            return {"message": "Queue workers status retrieved successfully", "workers": workers}

        except Exception as e:
            logging.error(f"Error getting supervisor status: {str(e)}")
            return {"error": str(e)}

    def parse_status_output(self, output):
        workers = []
        lines = output.splitlines()

        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                worker_name = parts[0]
                status = parts[1]

                try:
                    pid_index = parts.index('pid')
                    pid = parts[pid_index + 1].strip(',')
                    uptime = " ".join(parts[pid_index + 3:])
                except (ValueError, IndexError):
                    pid = None
                    uptime = "N/A"

                workers.append({
                    "worker_name": worker_name,
                    "status": status,
                    "pid": pid,
                    "uptime": uptime
                })
        return workers
