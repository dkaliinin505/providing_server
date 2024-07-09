from app.server_manager.interfaces.command_interface import Command
from utils.db_util import grant_privileges, create_user


class CreateDatabaseUserCommand(Command):
    def __init__(self, config):
        self.config = config

    async def execute(self, data):
        self.config = data
        await create_user(self.config)
        db_names = self.config.get('db_name', [])
        if isinstance(db_names, str):
            db_names = [db_names]

        if db_names:  # Check if db_names is not empty
            self.config['db_name'] = db_names
            await grant_privileges(self.config)

        return {"message": f"Database user created successfully: {self.config.get('db_user')}"}

