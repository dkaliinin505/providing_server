from app.server_manager.interfaces.command_interface import Command
from utils.db_util import grant_privileges, create_user
from utils.env_util import get_env_variable, async_get_env_variable
from utils.async_util import run_command_async


class CreateDatabaseCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config.update(data)
        await self.create_database()
        if self.config.get('create_user', False):
            await create_user(self.config)
            if 'db_privileges' in self.config:
                await grant_privileges(self.config)

        return {"message": f"Database created successfully: {self.config.get('db_name')}"}

    async def create_database(self):
        db_name = self.config.get('db_name')
        db_root_password = await async_get_env_variable('DB_PASSWORD')

        command = f'mysql --user="root" --password="{db_root_password}" -e "CREATE DATABASE `{db_name}` CHARACTER SET utf8 COLLATE utf8_unicode_ci;"'
        await run_command_async(command)
