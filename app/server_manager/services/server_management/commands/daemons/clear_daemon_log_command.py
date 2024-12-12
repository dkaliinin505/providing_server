from app.server_manager.interfaces.command_interface import Command
from utils.async_util import write_file_async
from pathlib import Path


class ClearDaemonLogsCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None

    async def execute(self, data):
        """
        Run the command with the given data.
        """
        self.config = data
        self.daemon_id = self.config.get('daemon_id')
        if not self.daemon_id:
            raise ValueError("daemon_id is required in the configuration.")

        user = self.config.get('user', 'super_forge')

        log_file = f'/home/{user}/.logs/daemon-{self.daemon_id}.log'
        log_path = Path(log_file)

        if not log_path.exists():
            raise FileNotFoundError(f"Log file for daemon {self.daemon_id} not found at {log_file}.")
        if not log_path.is_file():
            raise ValueError(f"Log path {log_file} is not a file.")

        try:
            await write_file_async(log_file, "")
            return {"message": 'Daemon Logs cleared successfully'}
        except Exception as e:
            raise Exception(f"Error clearing log file: {e}")
