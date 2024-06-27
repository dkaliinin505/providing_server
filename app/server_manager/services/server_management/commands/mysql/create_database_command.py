from app.server_manager.interfaces.command_interface import Command
from utils.db_util import grant_privileges, create_user
from utils.env_util import get_env_variable
from utils.util import run_command


class CreateDatabaseCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self, data):
        self.config.update(data)
        self.create_database()
        if self.config.get('create_user', False):
            create_user(self.config)
            if 'db_privileges' in self.config:
                grant_privileges(self.config)

    def create_database(self):
        db_name = self.config.get('db_name')
        db_root_password = self.config.get('db_root_password')

        command = f'mysql --user="root" --password="{db_root_password}" -e "CREATE DATABASE `{db_name}` CHARACTER SET utf8 COLLATE utf8_unicode_ci;"'
        run_command(command)
