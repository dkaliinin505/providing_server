from app.server_manager.services.server_management.commands.logs.clear_server_logs_command import ClearServerLogsCommand
from app.server_manager.services.server_management.commands.logs.get_server_logs_command import GetServerLogsCommand
from app.server_manager.services.service import Service


class ServerLogsService(Service):
    def __init__(self):
        super().__init__()
        self.executor.register('get_server_logs_command', GetServerLogsCommand({'config': {}}))
        self.executor.register('clear_server_logs_command', ClearServerLogsCommand({'config': {}}))

    async def get_server_logs(self, data):
        return await self.executor.execute('get_server_logs_command', data)

    async def clear_server_logs(self, data):
        return await self.executor.execute('clear_server_logs_command', data)
