from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class RemoveSSHKeyCommand(Command):
    def __init__(self, config):
        self.config = config
        self.user = None
        self.key_id = None

    async def execute(self, data):
        self.config = data
        self.user = self.config.get('user')
        self.key_id = self.config.get('key_id')

        # Define the SSH key file path
        authorized_keys_file = f"/home/{self.user}/.ssh/authorized_keys"

        # Command to remove the SSH key with the matching key ID
        remove_key_command = f'(sudo grep -v "# KEY_ID={self.key_id}" {authorized_keys_file}) > {authorized_keys_file}.tmp && mv {authorized_keys_file}.tmp {authorized_keys_file}'

        # Execute the command
        result = await run_command_async(remove_key_command, capture_output=True)

        if result:
            return {"message": f"SSH key with ID {self.key_id} removed successfully"}
        else:
            return {"error": f"Failed to remove SSH key"}
