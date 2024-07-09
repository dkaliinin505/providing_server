from app.server_manager.interfaces.command_interface import Command
from utils.db_util import create_user, grant_privileges


class UpdateDatabaseUserCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config.update(data)
        await create_user(self.config)
        if 'db_privileges' in self.config:
            await grant_privileges(self.config)
