class PackageInstaller:
    def __init__(self):
        self.commands = {}

    def register(self, package_name, command):
        self.commands[package_name] = command

    def install(self, package_name, data):
        command = self.commands.get(package_name)
        if command is None:
            return {"error": "Invalid package name"}
        return command.execute(data)
