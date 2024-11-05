import os
import uuid
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, read_file_async


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
        self.key_id = self.config.get('key_id', str(uuid.uuid4()))

        # Define the paths for key files
        ssh_dir = f"/home/{self.user}/.ssh"
        private_key_file = f"{ssh_dir}/id_rsa"
        public_key_file = f"{private_key_file}.pub"
        authorized_keys_file = f"{ssh_dir}/authorized_keys"

        # Ensure the .ssh directory exists
        os.makedirs(ssh_dir, exist_ok=True)

        # Generate SSH key pair
        keygen_command = f'ssh-keygen -t rsa -b 2048 -f {private_key_file} -N "" -C "{self.key_id}"'
        await run_command_async(keygen_command)

        # Read the generated private and public keys
        private_key = await read_file_async(private_key_file)
        public_key = await read_file_async(public_key_file)

        # Add a comment with the unique key ID before the provided SSH key to authorized_keys
        key_with_id = f"# KEY_ID={self.key_id}\n{self.ssh_key}"
        add_key_command = f'echo "{key_with_id}" | tee -a {authorized_keys_file}'
        result = await run_command_async(add_key_command, capture_output=True)

        if result:
            return {
                "message": "SSH key added successfully",
                "data": {
                    "id": self.key_id,
                    "public_key_data": public_key,
                    "private_key_data": private_key
                }
            }
        else:
            return {"error": "Failed to add SSH key"}
