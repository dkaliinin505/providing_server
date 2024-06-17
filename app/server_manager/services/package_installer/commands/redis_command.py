import os
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class RedisCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self, data):
        self.config = data.get('config', self.config)

        # Install Redis Server
        run_command("sudo apt-get install -y redis-server")

        # Update Redis configuration to bind to all interfaces
        run_command("sudo sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf")

        # Restart Redis service
        run_command("sudo service redis-server restart")

        # Enable Redis to start on boot
        run_command("sudo systemctl enable redis-server")

        # Install PHP Redis extension
        run_command("yes '' | sudo pecl install -f redis")

        # Ensure PHPRedis extension is available
        if self.is_phpredis_installed():
            print("Configuring PHPRedis")
            run_command("sudo sh -c 'echo \"extension=redis.so\" > /etc/php/8.3/mods-available/redis.ini'")
            run_command("yes '' | sudo apt install php8.3-redis")

        # Configure log rotation for Redis
        self.configure_log_rotation()

        return {"message": "Redis installed and configured"}

    @staticmethod
    def is_phpredis_installed():
        try:
            result = run_command("sudo pecl list | grep redis", return_json=False)
            return bool(result)
        except Exception:
            return False

    def configure_log_rotation(self):
        if self.file_contains("/etc/logrotate.d/redis-server", "maxsize"):
            self.update_or_append("/etc/logrotate.d/redis-server", "maxsize", "100M")
        else:
            run_command("sudo sed -i -r 's/^(\\s*)(daily|weekly|monthly|yearly)$/\\1\\2\\n\\1maxsize 100M/' /etc/logrotate.d/redis-server")

    @staticmethod
    def file_contains(file_path, text):
        try:
            with open(file_path, 'r') as file:
                return text in file.read()
        except FileNotFoundError:
            return False

    @staticmethod
    def append_to_file(file_path, text):
        with open(file_path, 'a') as file:
            file.write(text + "\n")

    @staticmethod
    def update_or_append(file_path, key, value):
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            updated = False
            for i, line in enumerate(lines):
                if line.startswith(key):
                    lines[i] = f"{key} = {value}\n"
                    updated = True
                    break

            if not updated:
                lines.append(f"{key} = {value}\n")

            with open(file_path, 'w') as file:
                file.writelines(lines)
        except FileNotFoundError:
            with open(file_path, 'w') as file:
                file.write(f"{key} = {value}\n")
