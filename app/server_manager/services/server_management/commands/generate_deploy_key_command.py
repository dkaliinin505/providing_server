import os
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class GenerateDeployKeyCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    def execute(self, data):
        self.config = data
        domain = self.config.get('domain')
        # SSH key path
        ssh_key_path = f'/home/super_forge/.ssh/{domain}'
        ssh_key_pub_path = f'{ssh_key_path}.pub'

        # Delete then Create config file for the GitHub
        run_command(f'sudo -u super_forge touch {ssh_key_path}-config')
        run_command(f'sudo -u super_forge echo "Host github.com" >> {ssh_key_path}-config')
        run_command(f'sudo -u super_forge echo "  User git" >> {ssh_key_path}-config')
        run_command(f'sudo -u super_forge echo "  IdentityFile {ssh_key_path}" >> {ssh_key_path}-config')
        run_command(f'sudo -u super_forge echo "  IdentitiesOnly yes" >> {ssh_key_path}-config')
        run_command(f'sudo chown super_forge /home/super_forge/.ssh/{domain}-config')
        run_command(f'sudo chmod 600 /home/super_forge/.ssh/{domain}-config')

        # Create .ssh directory
        if not os.path.exists('/home/super_forge/.ssh'):
            run_command('sudo -u super_forge mkdir -p /home/super_forge/.ssh')
            run_command('sudo -u super_forge chmod 700 /home/super_forge/.ssh')

        # Generate SSH key if it doesn't exist
        if not os.path.exists(ssh_key_path):
            run_command(f'sudo -u super_forge ssh-keygen -t rsa -b 4096 -f {ssh_key_path} -N ""')
            run_command(f'sudo -u super_forge chmod 600 {ssh_key_path}')
            run_command(f'sudo -u super_forge chmod 644 {ssh_key_pub_path}')

        # Read the public key
        with open(ssh_key_pub_path, 'r') as key_file:
            public_key = key_file.read()

        return {"message": "SSH key generated successfully", "public_key": public_key}
