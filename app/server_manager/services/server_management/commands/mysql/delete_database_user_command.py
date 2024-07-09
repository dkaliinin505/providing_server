from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async


class DeleteDatabaseUserCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        await self.config.update(data)
        await self.delete_database_user()

    async def delete_database_user(self):
        db_root_password = self.config.get('db_root_password')
        db_user = self.config.get('db_user')
        db_host = self.config.get('db_host', '%')

        commands = [
            f"mysql --user='root' --password='{db_root_password}' -e \"DROP USER IF EXISTS '{db_user}'@'{db_host}'; DROP USER IF EXISTS '{db_user}'@'%';\"",
            f"mysql --user='root' --password='{db_root_password}' -e \"DROP USER IF EXISTS '{db_user}'@'%'; DROP USER IF EXISTS '{db_user}'@'%';\""
        ]
        for command in commands:
            run_command_async(command)
