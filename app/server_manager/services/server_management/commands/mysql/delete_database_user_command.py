from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class DeleteDatabaseUserCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self, data):
        self.config.update(data)
        self.delete_database_user()

    def delete_database_user(self):
        db_root_password = self.config.get('db_root_password')
        db_user = self.config.get('db_user')
        db_host = self.config.get('db_host', '%')

        commands = [
            f"mysql --user='root' --password='{db_root_password}' -e \"DROP USER IF EXISTS '{db_user}'@'{db_host}'; DROP USER IF EXISTS '{db_user}'@'%';\"",
            f"mysql --user='root' --password='{db_root_password}' -e \"DROP USER IF EXISTS '{db_user}'@'%'; DROP USER IF EXISTS '{db_user}'@'%';\""
        ]
        for command in commands:
            run_command(command)
