import os

import requests

from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command, is_wsl


class MySQLCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    def execute(self, data):
        self.config = data.get('config', self.config)
        # Add MySQL Keys

        # Configure MySQL Repositories If Required
        ubuntu_version = run_command("lsb_release -rs")
        if self.version_to_int(ubuntu_version) <= self.version_to_int("20.04"):
            run_command("wget --no-check-certificate -c https://dev.mysql.com/get/mysql-apt-config_0.8.15-1_all.deb")
            run_command("dpkg --install mysql-apt-config_0.8.15-1_all.deb")
            run_command("apt-get update")

        # Set The Automated Root Password
        db_password = self.config.get('db_password', 'default_password')
        run_command(f'debconf-set-selections <<< "mysql-community-server mysql-community-server/data-dir select \'\'"')
        run_command(
            f'debconf-set-selections <<< "mysql-community-server mysql-community-server/root-pass password {db_password}"')
        run_command(
            f'debconf-set-selections <<< "mysql-community-server mysql-community-server/re-root-pass password {db_password}"')

        # Install MySQL

        # Add MySQL APT Repository
        run_command("apt-get update")
        run_command("apt-get install -y gnupg")
        run_command("mkdir -p /etc/apt/keyrings")
        run_command(
            "wget --quiet -O /etc/apt/keyrings/mysql-archive-keyring.gpg https://repo.mysql.com/RPM-GPG-KEY-mysql-2022")
        release_codename = run_command("lsb_release -cs")
        run_command(
            f'echo "deb [signed-by=/etc/apt/keyrings/mysql-archive-keyring.gpg] http://repo.mysql.com/apt/ubuntu/ {release_codename} mysql-8.0" | tee /etc/apt/sources.list.d/mysql.list')
        run_command("apt-get update")

        # Install MySQL
        run_command("DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server")

        # Start MySQL service if not running
        self.ensure_mysql_service_running()

        # Configure MySQL
        self.configure_mysql(db_password)


    def ensure_mysql_service_running(self):
        try:
            mysql_status = run_command("pgrep mysqld")
        except Exception as e:
            mysql_status = ""

        if not mysql_status:
            if is_wsl():
                try:
                    if run_command("pgrep mysqld", raise_exception=False):
                        run_command("pkill mysqld")
                    run_command("nohup mysqld_safe &", raise_exception=False)
                    # Wait a bit for the service to start
                    import time
                    time.sleep(5)
                    mysql_status = run_command("pgrep mysqld")
                    if not mysql_status:
                        raise Exception("Failed to start MySQL service.")
                except Exception as e:
                    raise Exception("Failed to start MySQL service.")
            else:
                try:
                    run_command("service mysql start")
                except Exception as e:
                    try:
                        run_command("service mysqld start")
                    except Exception as e:
                        try:
                            run_command("service mariadb start")
                        except Exception as e:
                            raise Exception("Failed to start MySQL service on non-WSL system.")

    def configure_mysql(self, db_password):
        # Configure Password Expiration
        self.append_to_file("/etc/mysql/mysql.conf.d/mysqld.cnf", "default_password_lifetime = 0")

        # Set Character Set
        self.append_to_file("/etc/mysql/my.cnf",
                            "\n[mysqld]\ndefault_authentication_plugin=mysql_native_password\nskip-log-bin")

        # Configure Max Connections
        ram = self.get_total_ram()
        max_connections = max(70 * ram, 100)
        self.update_or_append("/etc/mysql/my.cnf", "max_connections", max_connections)

        # Configure Access Permissions For Root & Forge Users
        self.configure_access_permissions(db_password)

        # Restart MySQL Service
        self.ensure_mysql_service_running()

        # Create Initial Database If Specified
        initial_db = self.config.get('initial_db', 'forge')
        run_command(
            f'mysql --user="root" --password="{db_password}" -e "CREATE DATABASE {initial_db} CHARACTER SET utf8 COLLATE utf8_unicode_ci;"')

        # Configure Log Rotation
        self.configure_log_rotation()

    def configure_access_permissions(self, db_password):
        # Modify bind-address
        if self.file_contains("/etc/mysql/mysql.conf.d/mysqld.cnf", "bind-address"):
            self.update_or_append("/etc/mysql/mysql.conf.d/mysqld.cnf", "bind-address", "*")
        else:
            self.append_to_file("/etc/mysql/mysql.conf.d/mysqld.cnf", "bind-address = *")

        # Create and Grant Permissions to Users
        self.create_and_grant_permissions(db_password, 'root')
        self.create_and_grant_permissions(db_password, 'super_forge')

    def create_and_grant_permissions(self, db_password, username):
        remote_ip = self.config.get('remote_ip', '3.78.19.112')
        commands = [
            f'CREATE USER \'{username}\'@\'{remote_ip}\' IDENTIFIED BY \'{db_password}\';',
            f'CREATE USER \'{username}\'@\'%\' IDENTIFIED BY \'{db_password}\';',
            f'GRANT ALL PRIVILEGES ON *.* TO \'{username}\'@\'{remote_ip}\' WITH GRANT OPTION;',
            f'GRANT ALL PRIVILEGES ON *.* TO \'{username}\'@\'%\' WITH GRANT OPTION;',
        ]
        for cmd in commands:
            run_command(f'mysql --user="root" --password="{db_password}" -e "{cmd}"')
        run_command(f'mysql --user="root" --password="{db_password}" -e "FLUSH PRIVILEGES;"')

    def configure_log_rotation(self):
        if self.file_contains("/etc/logrotate.d/mysql-server", "maxsize"):
            self.update_or_append("/etc/logrotate.d/mysql-server", "maxsize", "100M")
        else:
            self.append_to_file("/etc/logrotate.d/mysql-server", "maxsize 100M")

    @staticmethod
    def version_to_int(version):
        return int("".join(version.split(".")))

    @staticmethod
    def get_total_ram():
        ram_kb = int(run_command("awk '/^MemTotal:/{print $2}' /proc/meminfo"))
        ram_gb = ram_kb // (1024 * 1024)
        return ram_gb

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
