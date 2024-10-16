from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class ControlDaemonCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None
        self.action = None

    async def execute(self, data):
        self.daemon_id = data.get('daemon_id')
        self.action = data.get('action')  # 'start', 'stop', or 'restart'

        if self.action not in ['start', 'stop', 'restart']:
            raise Exception({"message": "Invalid action. Use 'start', 'stop', or 'restart'."})

        await run_command_async(f'sudo supervisorctl {self.action} {self.daemon_id}')

        return {"message": f"Daemon {self.daemon_id} {self.action}ed successfully.", "data": self.daemon_id}
