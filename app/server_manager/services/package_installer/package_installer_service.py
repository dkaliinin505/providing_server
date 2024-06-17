from app.server_manager.services.package_installer.commands.mysql_command import MySQLCommand
from app.server_manager.services.package_installer.commands.nginx_command import NginxCommand
from app.server_manager.services.package_installer.commands.php_command import PhpCommand
from app.server_manager.services.package_installer.commands.redis_command import RedisCommand
from app.server_manager.services.package_installer.invoker import PackageInstaller


class PackageInstallerService:
    def __init__(self):
        self.installer = PackageInstaller()
        self.installer.register('php', PhpCommand({'config': {}}))
        self.installer.register('nginx', NginxCommand({'config': {}}))
        self.installer.register('mysql', MySQLCommand({'config': {}}))
        self.installer.register('redis', RedisCommand({'config': {}}))

    def install_package(self, data):
        package_name = data.get('package_name')
        return self.installer.install(package_name, data)
