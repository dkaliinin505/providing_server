from app.server_manager.interfaces.invoker_interface import Invoker


class SiteManagementExecutor(Invoker):
    def __init__(self):
        self.commands = {}

    def register(self, name, command):
        self.commands[name] = command

    def execute(self, name, data):
        command = self.commands.get(name)
        if command is None:
            return {"error": "Invalid package name"}
        return command.execute(data)
