from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async
from utils.env_util import async_get_env_variable


class DeleteDatabaseUserCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config = data.get('config', self.config)
        await self.delete_database_user()

        return {"message": f"Database user deleted successfully: {self.config.get('db_user')}"}

    async def delete_database_user(self):
        db_root_password = async_get_env_variable('DB_PASSWORD')
        db_user = self.config.get('db_user')
        db_host = self.config.get('db_host', '%')

        commands = [
            f"mysql --user='root' --password='{db_root_password}' -e \"DROP USER IF EXISTS '{db_user}'@'%'; DROP USER IF EXISTS '{db_user}'@'%';\"",
            f"mysql --user='root' --password='{db_root_password}' -e \"DROP USER IF EXISTS '{db_user}'@'%'; DROP USER IF EXISTS '{db_user}'@'{db_host}';\""
        ]
        for command in commands:
            run_command_async(command)
