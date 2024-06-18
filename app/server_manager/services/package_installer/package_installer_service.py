from app.server_manager.services.package_installer.commands.mysql_command import MySQLCommand
from app.server_manager.services.package_installer.commands.nginx_command import NginxCommand
from app.server_manager.services.package_installer.commands.php_command import PhpCommand
from app.server_manager.services.package_installer.commands.redis_command import RedisCommand
from app.server_manager.services.package_installer.invoker import PackageExecutor


class PackageInstallerService:
    def __init__(self):
        self.executor = PackageExecutor()
        self.executor.register('php', PhpCommand({'config': {}}))
        self.executor.register('nginx', NginxCommand({'config': {}}))
        self.executor.register('mysql', MySQLCommand({'config': {}}))
        self.executor.register('redis', RedisCommand({'config': {}}))

    def install_package(self, data):
        package_name = data.get('package_name')
        return self.executor.execute(package_name, data)
