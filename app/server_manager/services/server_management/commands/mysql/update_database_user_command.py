from app.server_manager.interfaces.command_interface import Command
from utils.db_util import create_user, grant_privileges


class UpdateDatabaseUserCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self, data):
        self.config.update(data)
        create_user(self.config)
        if 'db_privileges' in self.config:
            grant_privileges(self.config)
