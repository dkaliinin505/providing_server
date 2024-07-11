from app.server_manager.services.invoker import CommandExecutor


class Service:
    def __init__(self):
        self.executor = CommandExecutor()

    def register_commands(self):
        raise NotImplementedError("Subclasses should implement this method to register their commands.")

    def cleanup(self):
        if hasattr(self, 'executor'):
            del self.executor

    def __del__(self):
        self.cleanup()
