from app.server_manager.interfaces.command_interface import Command
from utils.db_util import grant_privileges, create_user


class CreateDatabaseUserCommand(Command):
    def __init__(self, config):
        self.config = config

    def execute(self, data):
        self.config.update(data)
        create_user(self.config)
        grant_privileges(self.config)

