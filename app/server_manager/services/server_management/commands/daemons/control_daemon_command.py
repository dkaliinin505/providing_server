from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class ControlDaemonCommand(Command):
    def __init__(self, config):
        self.num_processes = None
        self.config = config
        self.daemon_id = None
        self.action = None

    async def execute(self, data):
        self.daemon_id = data.get('daemon_id')
        self.action = data.get('action')
        self.num_processes = int(data.get('num_processes', 1))

        if self.num_processes > 1:
            for i in range(self.num_processes):
                process_name = f"{self.daemon_id}:{self.daemon_id}_{i}"
                await run_command_async(f'sudo supervisorctl {self.action} {process_name}')
                print(f"Processed: {process_name} for action: {self.action}")
        else:
            await run_command_async(f'sudo supervisorctl {self.action} {self.daemon_id}')

        return {"message": f"Daemon {self.daemon_id} {self.action}ed successfully.", "data": self.daemon_id}
