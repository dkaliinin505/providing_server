from app.server_manager.interfaces.command_interface import Command
from utils.async_util import run_command_async, check_file_exists, dir_exists


class PhpCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    async def execute(self, data):
        self.config = data.get('config', {})

        await run_command_async("sudo apt-get update")

        # Install PHP 8.3
        await run_command_async(
            "sudo apt-get install -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold' -y --allow-downgrades --allow-remove-essential --allow-change-held-packages "
            "php8.3-fpm php8.3-cli php8.3-dev php8.3-pgsql php8.3-sqlite3 php8.3-gd php8.3-curl php8.3-imap php8.3-mysql php8.3-mbstring php8.3-xml php8.3-zip php8.3-bcmath php8.3-soap "
            "php8.3-intl php8.3-readline php8.3-gmp php8.3-redis php8.3-memcached php8.3-msgpack php8.3-igbinary php8.3-swoole"
        )

        # Composer installation
        if dir_exists("/usr/local/bin/composer"):
            await run_command_async("curl -sS https://getcomposer.org/installer | php")
            await run_command_async("sudo mv composer.phar /usr/local/bin/composer")
            await run_command_async(
                'echo "super_forge ALL=(root) NOPASSWD: /usr/local/bin/composer self-update*" | sudo tee /etc/sudoers.d/composer'
            )

        # Set up PHP CLI
        memory_limit = self.config.get('memory_limit', '512M')
        await run_command_async(
            'sudo sed -i "s/error_reporting = .*/error_reporting = E_ALL/" /etc/php/8.3/cli/php.ini')
        await run_command_async('sudo sed -i "s/display_errors = .*/display_errors = On/" /etc/php/8.3/cli/php.ini')
        await run_command_async('sudo sed -i "s/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/" /etc/php/8.3/cli/php.ini')
        await run_command_async(
            f'sudo sed -i "s/memory_limit = .*/memory_limit = {memory_limit}/" /etc/php/8.3/cli/php.ini')
        await run_command_async('sudo sed -i "s/;date.timezone.*/date.timezone = UTC/" /etc/php/8.3/cli/php.ini')

        # Set up PHP FPM
        await run_command_async('sudo sed -i "s/display_errors = .*/display_errors = Off/" /etc/php/8.3/fpm/php.ini')

        # Install Imagick
        await run_command_async("sudo apt-get install -y --force-yes libmagickwand-dev")
        await run_command_async(
            "echo 'extension=imagick.so' | sudo tee /etc/php/8.3/mods-available/imagick.ini > /dev/null")
        await run_command_async("yes '' | sudo apt install php8.3-imagick")

        # Set up PHP pool configuration
        await run_command_async('sudo sed -i "s/^user = www-data/user = super_forge/" /etc/php/8.3/fpm/pool.d/www.conf')
        await run_command_async(
            'sudo sed -i "s/^group = www-data/group = super_forge/" /etc/php/8.3/fpm/pool.d/www.conf')
        await run_command_async(
            'sudo sed -i "s/;listen\\.owner.*/listen.owner = super_forge/" /etc/php/8.3/fpm/pool.d/www.conf')
        await run_command_async(
            'sudo sed -i "s/;listen\\.group.*/listen.group = super_forge/" /etc/php/8.3/fpm/pool.d/www.conf')
        await run_command_async('sudo sed -i "s/;listen\\.mode.*/listen.mode = 0666/" /etc/php/8.3/fpm/pool.d/www.conf')
        await run_command_async(
            f'sudo sed -i "s/;request_terminate_timeout .*/request_terminate_timeout = {self.config["request_terminate_timeout"]}/" /etc/php/8.3/fpm/pool.d/www.conf'
        )

        max_children = self.config.get('pm_max_children', 20)
        # Optimize PHP FPM
        await run_command_async(
            f' sudo sed -i "s/^pm.max_children.*=.*/pm.max_children = {max_children}/" /etc/php/8.3/fpm/pool.d/www.conf'
        )

        # Refresh PHP FPM
        await run_command_async(
            'echo "super_forge ALL=NOPASSWD: /usr/sbin/service php8.3-fpm reload" | sudo tee -a /etc/sudoers.d/php-fpm'
        )

        # Set up session directory permissions
        await run_command_async("sudo chmod 733 /var/lib/php/sessions")
        await run_command_async("sudo chmod +t /var/lib/php/sessions")

        # Set up logrotate for PHP FPM
        logrotate_config = """
        /var/log/php8.3-fpm.log {
            daily
            missingok
            rotate 12
            compress
            delaycompress
            notifempty
            create 0640 root adm
            sharedscripts
            postrotate
                [ -f /var/run/php/php8.3-fpm.pid ] && kill -USR1 `cat /var/run/php/php8.3-fpm.pid`
            endscript
        }
        """
        await run_command_async(f'echo "{logrotate_config.strip()}" | sudo tee /etc/logrotate.d/php8.3-fpm')

        # Update PHP CLI to point to PHP 8.3
        await run_command_async("sudo update-alternatives --set php /usr/bin/php8.3")

        return {"message": "PHP installed and configured", "data": "8.3"}
