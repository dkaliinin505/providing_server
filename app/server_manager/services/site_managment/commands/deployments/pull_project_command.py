import asyncio
import os

import aiofiles

from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists, dir_exists, remove_ansi_escape_codes
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PullProjectCommand(Command):
    def __init__(self, config):
        self.config = config
        self.fpm_lock_path = "/tmp/fpmlock"

    async def execute(self, data):
        self.config = data
        await self.check_ubuntu_version()
        await self.setup_fpmlock()
        await self.source_env_file()
        await self.configure_ssh_command()
        data = await self.run_user_commands(self.config.get('user_script'))
        return {"message": f"Project {self.config.get('site')} pulled successfully.", "data": data}

    async def check_ubuntu_version(self):
        logger.debug("Checking Ubuntu version...")
        ubuntu_version = await run_command_async("lsb_release -rs")
        forge_version_check = lambda v: int("".join([f"{int(x):03}" for x in v.split(".")]))
        current_version = forge_version_check(ubuntu_version.strip())

        if current_version <= forge_version_check("16.04"):
            logger.debug(f"Your server is running an older version of Ubuntu ({ubuntu_version.strip()}).")
            logger.debug("We recommend provisioning a new server and migrating your sites.")
            return

    async def setup_fpmlock(self):
        logger.debug("Setting up FPM lock file...")
        fpm_lock = Path(self.fpm_lock_path)
        if not fpm_lock.exists():
            fpm_lock.touch()
            fpm_lock.chmod(0o666)

    async def source_env_file(self):
        logger.debug(f"Sourcing environment file from {self.config.get('site_path')}...")
        await run_command_async(f"set -o allexport; source {self.config.get('site_path')}/.env; set +o allexport")

    async def set_git_remote_url(self):
        github_username = self.config.get('github_username')
        repository_name = self.config.get('repository_name')

        if github_username and repository_name:
            git_remote_command = f"git remote set-url origin git@github.com:{github_username}/{repository_name}.git"
            logger.debug(f"Setting Git remote URL: {git_remote_command}")
            await run_command_async(git_remote_command)

    async def configure_ssh_command(self):
        # Configure SSH command to use the correct SSH config for the domain
        domain = self.config.get('site')
        ssh_config_path = f"/home/super_forge/.ssh/{domain}-config"
        ssh_command = f'export GIT_SSH_COMMAND="ssh -F {ssh_config_path}"'
        logger.debug(f"Setting SSH command for Git: {ssh_command}")
        await run_command_async(ssh_command)

    async def run_user_commands(self, commands_string: str):
        logger.debug("Running user-provided commands...")
        os.chdir(f"/home/super_forge/{self.config.get('site')}")

        await self.set_git_remote_url()
        commands_string = commands_string.replace('$FORGE_SITE_BRANCH', self.config.get('site_branch', 'master'))
        commands_string = commands_string.replace('$FORGE_COMPOSER',
                                                  self.config.get('composer', '/usr/local/bin/composer'))
        commands_string = commands_string.replace('$FORGE_PHP_FPM', self.config.get('php_fpm', 'php8.3-fpm'))
        commands_string = commands_string.replace('$FORGE_PHP', self.config.get('php', 'php8.3'))
        script_path = f"/tmp/{self.config.get('site')}_deploy.sh"

        async with aiofiles.open(script_path, 'w') as script_file:
            await script_file.write(commands_string)

        # Make the script executable
        await run_command_async(f'chmod +x {script_path}')

        # Run the script and capture output
        try:
            logger.debug(f"Executing deployment script: {script_path}")
            output = await run_command_async(script_path, capture_output=True)
            output = await remove_ansi_escape_codes(output)
            logger.debug(f"Deployment script output: {output}")
        except Exception as e:
            logger.error(f"Error executing deployment script: {str(e)}")
            output = f"Error: {str(e)}"

        # Clean up the script after execution
        await run_command_async(f'rm {script_path}')

        return output
