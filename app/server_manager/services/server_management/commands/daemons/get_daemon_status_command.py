from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class GetDaemonStatusCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None

    async def execute(self, data):
        self.daemon_id = data.get('daemon_id')

        try:
            result = await run_command_async(f'sudo supervisorctl status {self.daemon_id}', capture_output=True)

            return {
                "message": "Successfully retrieved daemon status",
                "data": result,
                "status": "success"
            }
        except Exception as e:
            return {
                "message": f"Successfully retrieved daemon status.",
                "data": str(e),
                "status": "success"
            }
