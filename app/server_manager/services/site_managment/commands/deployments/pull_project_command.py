import asyncio
from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists, dir_exists
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PullProjectCommand(Command):
    def __init__(self, config):
        self.config = config
        self.fpm_lock_path = "/tmp/fpmlock"

    def execute(self, data):
        self.config = data
        self.check_ubuntu_version()
        self.setup_fpmlock()
        self.source_env_file()
        self.run_user_commands(self.config.get('user_script'))

    async def check_ubuntu_version(self):
        logger.info("Checking Ubuntu version...")
        ubuntu_version = await run_command_async("lsb_release -rs")
        forge_version_check = lambda v: int("".join([f"{int(x):03}" for x in v.split(".")]))
        current_version = forge_version_check(ubuntu_version.strip())

        if current_version <= forge_version_check("16.04"):
            logger.warning(f"Your server is running an older version of Ubuntu ({ubuntu_version.strip()}).")
            logger.warning("We recommend provisioning a new server and migrating your sites.")
            return

    async def setup_fpmlock(self):
        logger.info("Setting up FPM lock file...")
        fpm_lock = Path(self.fpm_lock_path)
        if not fpm_lock.exists():
            fpm_lock.touch()
            fpm_lock.chmod(0o666)

    async def source_env_file(self):
        logger.info(f"Sourcing environment file from {self.config.get('site_path')}...")
        await run_command_async(f"set -o allexport; source {self.config.get('site_path')}/.env; set +o allexport")

    async def run_user_commands(self, commands_string: str):
        logger.info("Running user-provided commands...")

        commands = commands_string.split('\n')

        for command in commands:
            command = command.strip()
            if command:
                command = command.replace('$FORGE_SITE_BRANCH', self.config.get('site_branch', 'master'))
                command = command.replace('$FORGE_COMPOSER', self.config.get('composer', 'php8.3 /usr/local/bin/composer'))
                command = command.replace('$FORGE_PHP_FPM', self.config.get('php_fpm', 'php8.3-fpm'))
                command = command.replace('$FORGE_PHP', self.config.get('php', 'php8.3'))

                logger.info(f"Executing command: {command}")
                await run_command_async(command)

