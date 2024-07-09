from app.server_manager.interfaces.command_interface import Command
from utils.db_util import grant_privileges, create_user


class CreateDatabaseUserCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config.update(data)
        await create_user(self.config)
        if 'db_name' in self.config:
            await grant_privileges(self.config)

        return {"message": f"Database user created successfully: {self.config.get('db_user')}"}

