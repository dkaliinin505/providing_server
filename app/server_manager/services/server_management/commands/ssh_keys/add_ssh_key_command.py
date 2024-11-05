import os
import uuid
import pwd
import aiofiles
import asyncio
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
        self.key_id = self.config.get('key_id', str(uuid.uuid4()))

        ssh_dir = f"/home/{self.user}/.ssh"
        authorized_keys_file = f"{ssh_dir}/authorized_keys"

        key_with_id = f"# KEY_ID={self.key_id}\n{self.ssh_key}\n"

        # Command to append the SSH key with the unique ID to the authorized_keys file
        add_key_command = f'sudo echo "{key_with_id}" | tee -a {authorized_keys_file}'

        # Execute the command
        try:
            await run_command_async(add_key_command, capture_output=True)
            return {"message": f"SSH key added successfully", "key_id": self.key_id}

        except Exception as e:

            raise Exception({"message": f"Failed to add SSH key: {str(e)}"})
