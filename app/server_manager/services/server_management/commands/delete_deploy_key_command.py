import os
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class DeleteDeployKeyCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    def execute(self, data):
        # SSH key path
        ssh_key_path = f'/home/super_forge/.ssh/{self.config.get("domain")}'
        ssh_key_pub_path = f'{ssh_key_path}.pub'

        # Check if the key files exist and delete them
        if os.path.exists(ssh_key_path):
            run_command(f'sudo -u super_forge rm -f {ssh_key_path}')
            run_command(f'sudo -u super_forge rm -f {ssh_key_pub_path}')
            message = "SSH key deleted successfully"
        else:
            message = "SSH key not found"

        return {"message": message}
