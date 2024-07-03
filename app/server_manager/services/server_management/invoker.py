import asyncio

from app.server_manager.interfaces.invoker_interface import Invoker


class ServerManagementExecutor(Invoker):
    def __init__(self):
        self.commands = {}

    def register(self, name, command):
        self.commands[name] = command

    async def execute(self, name, data):
        command = self.commands.get(name)
        if command is None:
            return {"error": "Invalid package name"}

        if asyncio.iscoroutinefunction(command.execute):
            return await command.execute(data)
        else:
            return command.execute(data)
