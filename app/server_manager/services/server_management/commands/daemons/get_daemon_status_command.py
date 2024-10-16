from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class GetDaemonStatusCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None

    async def execute(self, data):
        self.daemon_id = data.get('daemon_id')

        result = await run_command_async(f'sudo supervisorctl status {self.daemon_id}', capture_output=True)

        if result:
            return {"message": "Successfully retrieved daemon status", "data": result}
        else:
            return {"error": f"Failed to retrieve status for Daemon {self.daemon_id}."}
