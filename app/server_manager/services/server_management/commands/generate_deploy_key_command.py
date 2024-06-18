import os
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class GenerateDeployKeyCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    def execute(self, data):
        # SSH key path
        ssh_key_path = f'/home/super_forge/.ssh/{self.config.get("domain")}'
        ssh_key_pub_path = f'{ssh_key_path}.pub'

        # Create .ssh directory
        if not os.path.exists('/home/super_forge/.ssh'):
            run_command('sudo -u super_forge mkdir -p /home/super_forge/.ssh')
            run_command('sudo -u super_forge chmod 700 /home/super_forge/.ssh')

        # Generate SSH key
        if not os.path.exists(ssh_key_path):
            run_command(f'sudo -u super_forge ssh-keygen -t rsa -b 4096 -f {ssh_key_path} -N ""')
            run_command(f'sudo -u super_forge chmod 600 {ssh_key_path}')
            run_command(f'sudo -u super_forge chmod 644 {ssh_key_pub_path}')

        # Read the public key
        with open(ssh_key_pub_path, 'r') as key_file:
            public_key = key_file.read()

        return {"message": "SSH key generated successfully", "public_key": public_key}
