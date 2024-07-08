import os
import aiofiles
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command_async


class RedisCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config = data.get('config', self.config)

        # Install Redis Server
        await run_command_async("sudo apt-get install -y redis-server")

        # Update Redis configuration to bind to all interfaces
        await run_command_async("sudo sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf")

        # Restart Redis service
        await run_command_async("sudo service redis-server restart")

        # Enable Redis to start on boot
        await run_command_async("sudo systemctl enable redis-server")

        # Install PHP Redis extension
        await run_command_async("yes '' | sudo pecl install -f redis")

        # Ensure PHPRedis extension is available
        if await self.is_phpredis_installed():
            print("Configuring PHPRedis")
            await run_command_async("sudo sh -c 'echo \"extension=redis.so\" > /etc/php/8.3/mods-available/redis.ini'")
            await run_command_async("yes '' | sudo apt install php8.3-redis")

        # Configure log rotation for Redis
        await self.configure_log_rotation()

        return {"message": "Redis installed and configured"}

    @staticmethod
    async def is_phpredis_installed():
        try:
            result = await run_command_async("sudo pecl list | grep redis")
            return bool(result)
        except Exception:
            return False

    async def configure_log_rotation(self):
        if await self.file_contains("/etc/logrotate.d/redis-server", "maxsize"):
            await self.update_or_append("/etc/logrotate.d/redis-server", "maxsize", "100M")
        else:
            await run_command_async(
                "sudo sed -i -r 's/^(\\s*)(daily|weekly|monthly|yearly)$/\\1\\2\\n\\1maxsize 100M/' /etc/logrotate.d/redis-server")

    @staticmethod
    async def file_contains(file_path, text):
        try:
            async with aiofiles.open(file_path, 'r') as file:
                content = await file.read()
            return text in content
        except FileNotFoundError:
            return False

    @staticmethod
    async def append_to_file(file_path, text):
        async with aiofiles.open(file_path, 'a') as file:
            await file.write(text + "\n")

    @staticmethod
    async def update_or_append(file_path, key, value):
        try:
            async with aiofiles.open(file_path, 'r') as file:
                lines = await file.readlines()

            updated = False
            for i, line in enumerate(lines):
                if line.startswith(key):
                    lines[i] = f"{key} = {value}\n"
                    updated = True
                    break

            if not updated:
                lines.append(f"{key} = {value}\n")

            async with aiofiles.open(file_path, 'w') as file:
                await file.writelines(lines)
        except FileNotFoundError:
            async with aiofiles.open(file_path, 'w') as file:
                await file.write(f"{key} = {value}\n")
