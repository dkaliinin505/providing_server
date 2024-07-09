from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async
from utils.env_util import async_get_env_variable
from utils.util import run_command


class DeleteDatabaseCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config = data
        await self.delete_database()

        return {"message": f"Database deleted successfully: {self.config.get('db_name')}"}

    async def delete_database(self):
        db_root_password = await async_get_env_variable('DB_PASSWORD')
        db_name = self.config.get('db_name')

        command = f"mysql --user='root' --password='{db_root_password}' -e \"DROP DATABASE IF EXISTS {db_name};\""
        await run_command_async(command)
