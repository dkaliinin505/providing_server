import os
import uuid
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class AddSSHKeyCommand(Command):
    def __init__(self, config):
        self.config = config
        self.user = None
        self.ssh_key = None
        self.key_id = None

    async def execute(self, data):
        self.config = data
        self.user = self.config.get('user')
        self.ssh_key = self.config.get('ssh_key')
        self.key_id = str(uuid.uuid4())  # Generate a unique ID for the SSH key

        # Define the SSH key file path
        authorized_keys_file = f"/home/{self.user}/.ssh/authorized_keys"
        os.makedirs(f"/home/{self.user}/.ssh", exist_ok=True)

        # Add a comment with the unique key ID before the SSH key
        key_with_id = f"# KEY_ID={self.key_id}\n{self.ssh_key}"

        # Command to append the SSH key with the unique ID to the authorized_keys file
        add_key_command = f'echo "{key_with_id}" | tee -a {authorized_keys_file}'

        # Execute the command
        result = await run_command_async(add_key_command, capture_output=True)

        if result:
            return {"message": f"SSH key added successfully", "key_id": self.key_id}
        else:
            return {"error": f"Failed to add SSH key"}

