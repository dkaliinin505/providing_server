from app.server_manager.services.server_management.invoker import ServerManagementExecutor


class Service:
    def __init__(self):
        self.executor = ServerManagementExecutor()

    def register_commands(self):
        raise NotImplementedError("Subclasses should implement this method to register their commands.")

    def cleanup(self):
        if hasattr(self, 'executor'):
            del self.executor

    def __del__(self):
        self.cleanup()
