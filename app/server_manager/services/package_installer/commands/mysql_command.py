import logging
import os
import aiofiles
import asyncio
from app.server_manager.interfaces.command_interface import Command
from utils.util import is_wsl
from utils.async_util import run_command_async, check_file_exists, dir_exists
from utils.env_util import update_env_variable, async_load_env, async_update_env_variable, async_get_env_variable

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MySQLCommand(Command):
    def __init__(self, config):
        self.config = config
        asyncio.run(async_load_env())
        print(f"Config: {config}")

    async def execute(self, data):
        self.config = data.get('config', self.config)

        # Configure MySQL Repositories If Required
        ubuntu_version = (await run_command_async("lsb_release -rs")).strip()
        if self.version_to_int(ubuntu_version) <= self.version_to_int("20.04"):
            print("Configuring MySQL Repositories for Ubuntu 20.04 and below")
            await run_command_async(
                "sudo wget --no-check-certificate -c https://dev.mysql.com/get/mysql-apt-config_0.8.15-1_all.deb")
            await run_command_async("sudo dpkg --install mysql-apt-config_0.8.15-1_all.deb")
            await run_command_async("sudo apt-get update")

        # Set The Automated Root Password
        db_password = await async_get_env_variable('DB_PASSWORD')
        await run_command_async(
            f"echo 'mysql-community-server mysql-community-server/data-dir select \"\"' | sudo debconf-set-selections")
        await run_command_async(
            f"echo 'mysql-community-server mysql-community-server/root-pass password {db_password}' | sudo debconf-set-selections")
        await run_command_async(
            f"echo 'mysql-community-server mysql-community-server/re-root-pass password {db_password}' | sudo debconf-set-selections")

        # Add MySQL APT Repository
        await run_command_async("sudo apt-get install -y gnupg")
        await run_command_async(
            "sudo wget --no-check-certificate -q -O - https://repo.mysql.com/RPM-GPG-KEY-mysql-2022 | sudo apt-key add -")
        await run_command_async(
            'echo "deb http://repo.mysql.com/apt/ubuntu/ $(lsb_release -cs) mysql-8.0" | sudo tee /etc/apt/sources.list.d/mysql.list')

        # Update package lists
        try:
            await run_command_async("sudo apt-get update")
        except Exception as e:
            print("Failed to update package lists. Attempting to fix missing keys.")
            await run_command_async("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B7B3B788A8D3785C")
            await run_command_async("sudo apt-get update")

        # Install MySQL with non-interactive frontend
        await run_command_async("DEBIAN_FRONTEND=noninteractive sudo -E apt-get install -y mysql-server",
                                raise_exception=True)

        # Start MySQL service if not running
        await self.ensure_mysql_service_running()

        # Configure MySQL
        await self.configure_mysql(db_password)

        # Update .env file with new MySQL credentials
        await async_update_env_variable("DB_PASSWORD", db_password)

        return {"message": "MySQL installed and configured"}

    async def ensure_mysql_service_running(self):
        try:
            mysql_status = await run_command_async("pgrep mysqld", raise_exception=False)
        except Exception as e:
            mysql_status = ""

        if not mysql_status:
            if is_wsl():
                try:
                    if await run_command_async("sudo pgrep mysqld", raise_exception=False):
                        await run_command_async("sudo pkill mysqld")
                    await run_command_async("sudo nohup mysqld_safe &", raise_exception=False)
                    # Wait a bit for the service to start
                    await asyncio.sleep(5)
                    mysql_status = await run_command_async("sudo pgrep mysqld")
                    if not mysql_status:
                        raise Exception("Failed to start MySQL service.")
                except Exception as e:
                    raise Exception("Failed to start MySQL service.")
            else:
                try:
                    await run_command_async("sudo service mysql start")
                except Exception as e:
                    try:
                        await run_command_async("sudo service mysqld start")
                    except Exception as e:
                        try:
                            await run_command_async("sudo service mariadb start")
                        except Exception as e:
                            raise Exception("Failed to start MySQL service on non-WSL system.")

    async def configure_mysql(self, db_password):
        # Configure Password Expiration
        await self.append_to_file("/etc/mysql/mysql.conf.d/mysqld.cnf", "default_password_lifetime = 0")

        # Set Character Set
        await self.append_to_file("/etc/mysql/my.cnf",
                                  "\n[mysqld]\ndefault_authentication_plugin=mysql_native_password\nskip-log-bin")

        # Configure Max Connections
        ram = await self.get_total_ram()
        max_connections = max(70 * ram, 100)
        await self.update_or_append("/etc/mysql/my.cnf", "max_connections", max_connections)

        # Configure Access Permissions For Root & Forge Users
        await self.configure_access_permissions(db_password)

        # Restart MySQL Service
        await self.ensure_mysql_service_running()

        # Create Initial Database If Specified
        initial_db = self.config.get('initial_db', 'forge')
        await run_command_async(
            f'sudo mysql --user="root" --password="{db_password}" -e "CREATE DATABASE {initial_db} CHARACTER SET utf8 COLLATE utf8_unicode_ci;"')

        # Configure Log Rotation
        await self.configure_log_rotation()

    async def configure_access_permissions(self, db_password):
        # Modify bind-address
        if await self.file_contains("/etc/mysql/mysql.conf.d/mysqld.cnf", "bind-address"):
            await self.update_or_append("/etc/mysql/mysql.conf.d/mysqld.cnf", "bind-address", "*")
        else:
            await self.append_to_file("/etc/mysql/mysql.conf.d/mysqld.cnf", "bind-address = *")

        # Create and Grant Permissions to Users
        await self.create_and_grant_permissions(db_password, 'root')
        await self.create_and_grant_permissions(db_password, 'super_forge')

    async def create_and_grant_permissions(self, db_password, username):
        remote_ip = self.config.get('remote_ip', '3.78.19.112')
        commands = [
            f'CREATE USER \'{username}\'@\'{remote_ip}\' IDENTIFIED BY \'{db_password}\';',
            f'CREATE USER \'{username}\'@\'%\' IDENTIFIED BY \'{db_password}\';',
            f'GRANT ALL PRIVILEGES ON *.* TO \'{username}\'@\'{remote_ip}\' WITH GRANT OPTION;',
            f'GRANT ALL PRIVILEGES ON *.* TO \'{username}\'@\'%\' WITH GRANT OPTION;',
        ]
        for cmd in commands:
            await run_command_async(f'sudo mysql --user="root" --password="{db_password}" -e "{cmd}"')
        await run_command_async(f'sudo mysql --user="root" --password="{db_password}" -e "FLUSH PRIVILEGES;"')

    async def configure_log_rotation(self):
        if await self.file_contains("/etc/logrotate.d/mysql-server", "maxsize"):
            await self.update_or_append("/etc/logrotate.d/mysql-server", "maxsize", "100M")
        else:
            await self.append_to_file("/etc/logrotate.d/mysql-server", "maxsize 100M")

    @staticmethod
    def version_to_int(version):
        return int("".join(version.split(".")))

    async def get_total_ram(self):
        ram_kb = int(await run_command_async("awk '/^MemTotal:/{print $2}' /proc/meminfo"))
        ram_gb = ram_kb // (1024 * 1024)
        return ram_gb

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
        await run_command_async(f'echo "{text}" | sudo tee -a {file_path} > /dev/null')

    @staticmethod
    async def update_or_append(file_path, key, value):
        try:
            lines = (await run_command_async(f'sudo cat {file_path}')).splitlines()
            updated = False
            for i, line in enumerate(lines):
                if line.startswith(key):
                    lines[i] = f"{key} = {value}"
                    updated = True
                    break

            if not updated:
                lines.append(f"{key} = {value}")

            await run_command_async(f'echo "{os.linesep.join(lines)}" | sudo tee {file_path} > /dev/null')
        except FileNotFoundError:
            await run_command_async(f'echo "{key} = {value}" | sudo tee {file_path} > /dev/null')
