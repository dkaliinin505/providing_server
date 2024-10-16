from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class GetDaemonStatusCommand(Command):
    def __init__(self, config):
        self.config = config
        self.daemon_id = None

    async def execute(self, data):
        self.daemon_id = data.get('daemon_id')

        result, error_output = await run_command_async(
            f'sudo supervisorctl status {self.daemon_id}',
            capture_output=True,
            raise_exception=False
        )

        if error_output:
            return {
                "message": f"Successfully retrieved daemon status.",
                "data": error_output,
                "status": "error"
            }
        else:
            return {
                "message": "Successfully retrieved daemon status",
                "data": result,
                "status": "success"
            }
