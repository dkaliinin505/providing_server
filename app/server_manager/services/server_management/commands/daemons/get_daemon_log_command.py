from app.server_manager.interfaces.command_interface import Command
from utils.async_util import read_file_async, read_last_lines_async


class GetDaemonLogsCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None

    async def execute(self, data):
        self.config = data
        self.daemon_id = self.config.get('daemon_id')
        log_file = f'/home/{self.config.get("user", "root")}/.logs/daemon-{self.daemon_id}.log'

        log_content = await read_last_lines_async(log_file, 500)

        if log_content:
            return {"message": 'Daemon Logs retrieved successfully', "data": '\n'.join(log_content)}
        else:
            return {"error": f"Log file for Daemon {self.daemon_id} not found."}
