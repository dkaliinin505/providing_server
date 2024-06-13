import os

from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class PhpCommand(Command):
    def execute(self, data):
        config = data.get('config', {})

        run_command("sudo apt-get update")

        # Install PHP 8.3
        run_command(
            "sudo apt-get install -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold' -y --allow-downgrades --allow-remove-essential --allow-change-held-packages "
            "php8.3-fpm php8.3-cli php8.3-dev php8.3-pgsql php8.3-sqlite3 php8.3-gd php8.3-curl php8.3-imap php8.3-mysql php8.3-mbstring php8.3-xml php8.3-zip php8.3-bcmath php8.3-soap "
            "php8.3-intl php8.3-readline php8.3-gmp php8.3-redis php8.3-memcached php8.3-msgpack php8.3-igbinary php8.3-swoole"
        )

        # Composer installation
        if not os.path.exists("/usr/local/bin/composer"):
            run_command("curl -sS https://getcomposer.org/installer | php")
            run_command("sudo mv composer.phar /usr/local/bin/composer")
            run_command(
                'echo "super_forge ALL=(root) NOPASSWD: /usr/local/bin/composer self-update*" | sudo tee /etc/sudoers.d/composer'
            )

        # Set up PHP CLI
        run_command('sudo sed -i "s/error_reporting = .*/error_reporting = E_ALL/" /etc/php/8.3/cli/php.ini')
        run_command('sudo sed -i "s/display_errors = .*/display_errors = On/" /etc/php/8.3/cli/php.ini')
        run_command('sudo sed -i "s/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/" /etc/php/8.3/cli/php.ini')
        run_command(
            f'sudo sed -i "s/memory_limit = .*/memory_limit = {config["memory_limit"]}/" /etc/php/8.3/cli/php.ini')
        run_command('sudo sed -i "s/;date.timezone.*/date.timezone = UTC/" /etc/php/8.3/cli/php.ini')

        # Set up PHP FPM
        run_command('sudo sed -i "s/display_errors = .*/display_errors = Off/" /etc/php/8.3/fpm/php.ini')

        # Install Imagick
        run_command("sudo apt-get install -y --force-yes libmagickwand-dev")
        run_command("echo 'extension=imagick.so' | sudo tee /etc/php/8.3/mods-available/imagick.ini > /dev/null")
        run_command("yes '' | sudo apt install php8.3-imagick")

        # Set up PHP pool configuration
        run_command('sudo sed -i "s/^user = www-data/user = super_forge/" /etc/php/8.3/fpm/pool.d/www.conf')
        run_command('sudo sed -i "s/^group = www-data/group = super_forge/" /etc/php/8.3/fpm/pool.d/www.conf')
        run_command('sudo sed -i "s/;listen\\.owner.*/listen.owner = super_forge/" /etc/php/8.3/fpm/pool.d/www.conf')
        run_command('sudo sed -i "s/;listen\\.group.*/listen.group = super_forge/" /etc/php/8.3/fpm/pool.d/www.conf')
        run_command('sudo sed -i "s/;listen\\.mode.*/listen.mode = 0666/" /etc/php/8.3/fpm/pool.d/www.conf')
        run_command(
            f'sudo sed -i "s/;request_terminate_timeout .*/request_terminate_timeout = {config["request_terminate_timeout"]}/" /etc/php/8.3/fpm/pool.d/www.conf'
        )

        # Optimize PHP FPM
        run_command(
            f' sudo sed -i "s/^pm.max_children.*=.*/pm.max_children = {config["pm_max_children"]}/" /etc/php/8.3/fpm/pool.d/www.conf'
        )

        # Refresh PHP FPM
        run_command(
            'echo "forge ALL=NOPASSWD: /usr/sbin/service php8.3-fpm reload" | sudo tee -a /etc/sudoers.d/php-fpm')

        # Set up session directory permissions
        run_command("sudo chmod 733 /var/lib/php/sessions")
        run_command("sudo chmod +t /var/lib/php/sessions")

        # Set up logrotate for PHP FPM
        file_exists = run_command('test -f /etc/logrotate.d/php8.3-fpm && echo "exists"', return_json=False)
        if file_exists.strip() == "exists":
            grep_output = run_command(
                'grep --count "maxsize" /etc/logrotate.d/php8.3-fpm', return_json=False, raise_exception=False
            )
            if grep_output is None or grep_output.strip() == "0":
                with open('/etc/logrotate.d/php8.3-fpm', 'r') as file:
                    lines = file.readlines()

                with open('/etc/logrotate.d/php8.3-fpm', 'w') as file:
                    for line in lines:
                        file.write(line)
                        if line.strip() in ['daily', 'weekly', 'monthly', 'yearly']:
                            file.write('maxsize 100M\n')
        else:
            # Create logrotate file for PHP FPM
            with open('/etc/logrotate.d/php8.3-fpm', 'w') as f:
                f.write('daily\nmaxsize 100M\n')

        # Update PHP CLI to point to PHP 8.3
        run_command("sudo update-alternatives --set php /usr/bin/php8.3")

        return {"message": "PHP installed and configured"}

