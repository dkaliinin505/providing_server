from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async
from utils.util import run_command


class DeleteDatabaseCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        await self.config.update(data)
        await self.delete_database()

    async def delete_database(self):
        db_root_password = self.config.get('db_root_password')
        db_name = self.config.get('db_name')

        command = f"mysql --user='root' --password='{db_root_password}' -e \"DROP DATABASE IF EXISTS {db_name};\""
        run_command_async(command)
