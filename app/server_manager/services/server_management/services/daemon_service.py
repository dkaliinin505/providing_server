from app.server_manager.services.server_management.commands.daemons.control_daemon_command import ControlDaemonCommand
from app.server_manager.services.server_management.commands.daemons.create_daemon_command import CreateDaemonCommand
from app.server_manager.services.server_management.commands.daemons.delete_daemon_command import DeleteDaemonCommand
from app.server_manager.services.server_management.commands.daemons.get_daemon_log_command import GetDaemonLogsCommand
from app.server_manager.services.server_management.commands.daemons.get_daemon_status_command import \
    GetDaemonStatusCommand
from app.server_manager.services.server_management.commands.daemons.update_daemon_command import UpdateDaemonCommand
from app.server_manager.services.service import Service


class DaemonService(Service):

    def __init__(self):
        super().__init__()
        self.executor.register('create_daemon_command', CreateDaemonCommand({'config': {}}))
        self.executor.register('update_daemon_command', UpdateDaemonCommand({'config': {}}))
        self.executor.register('delete_daemon_command', DeleteDaemonCommand({'config': {}}))
        self.executor.register('get_daemon_status_command', GetDaemonStatusCommand({'config': {}}))
        self.executor.register('control_daemon_command', ControlDaemonCommand({'config': {}}))
        self.executor.register('get_daemon_logs_command', GetDaemonLogsCommand({'config': {}}))

    async def create_daemon(self, data):
        return await self.executor.execute('create_daemon_command', data)

    async def update_daemon(self, data):
        return await self.executor.execute('update_daemon_command', data)

    async def delete_daemon(self, data):
        return await self.executor.execute('delete_daemon_command', data)

    async def get_daemon_status(self, data):
        return await self.executor.execute('get_daemon_status_command', data)

    async def control_daemon(self, data):
        return await self.executor.execute('control_daemon_command', data)

    async def get_daemon_logs(self, data):
        return await self.executor.execute('get_daemon_logs_command', data)


