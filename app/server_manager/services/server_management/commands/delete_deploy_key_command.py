from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command_async, check_file_exists


class DeleteDeployKeyCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    async def execute(self, data):
        self.config = data
        domain = self.config.get('domain')
        # SSH key path
        ssh_key_path = f'/home/super_forge/.ssh/{domain}'
        ssh_key_pub_path = f'{ssh_key_path}.pub'

        # Delete the config file for the GitHub
        if await check_file_exists(f'{ssh_key_path}-config'):
            await run_command_async(f'sudo -u super_forge rm -f {ssh_key_path}-config')

        # Check if the key files exist and delete them
        if await check_file_exists(ssh_key_path):
            await run_command_async(f'sudo -u super_forge rm -f {ssh_key_path}')
            await run_command_async(f'sudo -u super_forge rm -f {ssh_key_pub_path}')
            message = "SSH key deleted successfully"
        else:
            message = "SSH key not found"

        return {"message": message}
