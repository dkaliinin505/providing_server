import aiofiles
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command_async, file_exists, dir_exists
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class GenerateDeployKeyCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    async def execute(self, data):
        self.config = data
        domain = self.config.get('domain')
        # SSH key path
        ssh_key_path = f'/home/super_forge/.ssh/{domain}'
        ssh_key_pub_path = f'{ssh_key_path}.pub'

        # Create .ssh directory if it doesn't exist
        ssh_dir = '/home/super_forge/.ssh'
        if not await dir_exists(ssh_dir):
            await run_command_async(f'sudo -u super_forge mkdir -p {ssh_dir}')
            await run_command_async(f'sudo -u super_forge chmod 700 {ssh_dir}')
        else:
            logger.debug(f"The directory {ssh_dir} already exists")

        # Delete then Create config file for GitHub
        await run_command_async(f'sudo -u super_forge touch {ssh_key_path}-config')
        await run_command_async(f'sudo -u super_forge echo "Host github.com" >> {ssh_key_path}-config')
        await run_command_async(f'sudo -u super_forge echo "  User git" >> {ssh_key_path}-config')
        await run_command_async(f'sudo -u super_forge echo "  IdentityFile {ssh_key_path}" >> {ssh_key_path}-config')
        await run_command_async(f'sudo -u super_forge echo "  IdentitiesOnly yes" >> {ssh_key_path}-config')
        await run_command_async(f'sudo chown super_forge /home/super_forge/.ssh/{domain}-config')
        await run_command_async(f'sudo chmod 600 /home/super_forge/.ssh/{domain}-config')

        # Generate SSH key if it doesn't exist
        if not await file_exists(ssh_key_path):
            await run_command_async(f'sudo -u super_forge ssh-keygen -t rsa -b 4096 -f {ssh_key_path} -N ""')
            await run_command_async(f'sudo -u super_forge chmod 600 {ssh_key_path}')
            await run_command_async(f'sudo -u super_forge chmod 644 {ssh_key_pub_path}')
        else:
            logger.debug(f"The SSH key {ssh_key_path} already exists")

        # Read the public key
        async with aiofiles.open(ssh_key_pub_path, 'r') as key_file:
            public_key = await key_file.read()

        return {"message": "SSH key generated successfully", "public_key": public_key}
