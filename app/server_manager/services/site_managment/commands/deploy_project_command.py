import os
import json
import shutil
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command


class DeploySiteCommand(Command):
    def __init__(self, config):
        self.config = config
        print(f"Config: {config}")

    def execute(self, data):
        self.config = data
        domain = self.config.get('domain')
        repository_url = self.config.get('repository_url')
        branch = self.config.get('branch', 'master')
        ssh_command = f'ssh -F /home/super_forge/.ssh/{domain}-config'
        site_path = f'/home/super_forge/{domain}'
        nested_structure = self.config.get('nested_structure', False)
        nested_folder = self.config.get('nested_folder', 'app')

        # Remove The Current Site Directory
        if os.path.exists(site_path):
            shutil.rmtree(site_path)

        # Clone The Repository Into The Site
        self.clone_repository(repository_url, branch, site_path, ssh_command, nested_structure, nested_folder)

        # Install Composer Dependencies If Requested
        self.install_composer_dependencies(site_path, nested_structure, nested_folder)

        # Create Environment File If Necessary
        self.create_env_file(site_path, domain, nested_structure, nested_folder)

        # Run Artisan Migrations If Requested
        self.run_migrations(site_path, nested_structure, nested_folder)

        return {"message": "Site deployed successfully"}

    def clone_repository(self, repository_url, branch, site_path, ssh_command, nested_structure, nested_folder):
        git_command = f'git clone --depth 1 --single-branch -c core.sshCommand="{ssh_command}" -b {branch} {repository_url} {site_path}'
        run_command(git_command)
        os.chdir(site_path)
        run_command(f'git config core.sshCommand "{ssh_command}"')
        run_command('git submodule update --init --recursive')
        if nested_structure:
            os.chdir(os.path.join(site_path, nested_folder))

    def install_composer_dependencies(self, site_path, nested_structure, nested_folder):
        if nested_structure:
            os.chdir(os.path.join(site_path, nested_folder))
        else:
            os.chdir(site_path)
        run_command('php8.3 /usr/local/bin/composer install --no-interaction --prefer-dist --optimize-autoloader')

    def create_env_file(self, site_path, domain, nested_structure, nested_folder):
        if nested_structure:
            site_path = os.path.join(site_path, nested_folder)
        laravel_version = self.get_laravel_version(site_path)
        env_file_path = os.path.join(site_path, '.env')

        if os.path.isfile(os.path.join(site_path, '.env.example')):
            shutil.copyfile(os.path.join(site_path, '.env.example'), env_file_path)
        else:
            env_content = self.generate_env_content(laravel_version)
            with open(env_file_path, 'w') as env_file:
                env_file.write(env_content)

        self.update_env_file(env_file_path, laravel_version, domain)

    def get_laravel_version(self, site_path):
        composer_json_path = os.path.join(site_path, 'composer.json')
        with open(composer_json_path) as f:
            composer_data = json.load(f)
        laravel_version = composer_data.get('require', {}).get('laravel/framework', '0.0.0')
        return int(laravel_version.split('.')[0])

    def generate_env_content(self, laravel_version):
        if laravel_version >= 11:
            return """APP_NAME=Laravel
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_TIMEZONE=UTC
APP_URL=http://localhost

APP_LOCALE=en
APP_FALLBACK_LOCALE=en
APP_FAKER_LOCALE=en_US

APP_MAINTENANCE_DRIVER=file
APP_MAINTENANCE_STORE=database

LOG_CHANNEL=stack
LOG_STACK=single
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=sqlite
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_DATABASE=
# DB_USERNAME=forge
# DB_PASSWORD=""

BROADCAST_CONNECTION=log
CACHE_STORE=database
FILESYSTEM_DISK=local
QUEUE_CONNECTION=database
SESSION_DRIVER=database
SESSION_LIFETIME=120

MEMCACHED_HOST=127.0.0.1

REDIS_CLIENT=phpredis
REDIS_HOST=127.0.0.1
REDIS_PASSWORD=""
REDIS_PORT=6379

MAIL_MAILER=log
MAIL_HOST=127.0.0.1
MAIL_PORT=2525
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS="hello@example.com"
MAIL_FROM_NAME="${APP_NAME}"

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=
AWS_USE_PATH_STYLE_ENDPOINT=false

PUSHER_APP_ID=
PUSHER_APP_KEY=
PUSHER_APP_SECRET=
PUSHER_HOST=
PUSHER_PORT=443
PUSHER_SCHEME=https
PUSHER_APP_CLUSTER=mt1

VITE_APP_NAME="${APP_NAME}"
VITE_PUSHER_APP_KEY="${PUSHER_APP_KEY}"
VITE_PUSHER_HOST="${PUSHER_HOST}"
VITE_PUSHER_PORT="${PUSHER_PORT}"
VITE_PUSHER_SCHEME="${PUSHER_SCHEME}"
VITE_PUSHER_APP_CLUSTER="${PUSHER_APP_CLUSTER}"
"""
        else:
            return """APP_NAME=Laravel
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_URL=http://localhost

LOG_CHANNEL=stack

DB_CONNECTION=
DB_HOST=127.0.0.1
DB_PORT=
DB_DATABASE=
DB_USERNAME=forge
DB_PASSWORD=""

BROADCAST_DRIVER=log
CACHE_DRIVER=file
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120

REDIS_HOST=127.0.0.1
REDIS_PASSWORD=""
REDIS_PORT=6379

MAIL_DRIVER=smtp
MAIL_HOST=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
MAIL_FROM_ADDRESS=null
MAIL_FROM_NAME="${APP_NAME}"

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=

PUSHER_APP_ID=
PUSHER_APP_KEY=
PUSHER_APP_SECRET=
PUSHER_APP_CLUSTER=mt1

VITE_PUSHER_APP_KEY="${PUSHER_APP_KEY}"
VITE_PUSHER_HOST="${PUSHER_HOST}"
VITE_PUSHER_PORT="${PUSHER_PORT}"
VITE_PUSHER_SCHEME="${PUSHER_SCHEME}"
VITE_PUSHER_APP_CLUSTER="${PUSHER_APP_CLUSTER}"
"""

    def update_env_file(self, env_file_path, laravel_version, domain):
        with open(env_file_path, 'r') as file:
            env_data = file.readlines()

        env_data = [line.replace('APP_ENV=', 'APP_ENV=production\n') if line.startswith('APP_ENV=') else line for line in env_data]
        env_data = [line.replace('APP_URL=', f'APP_URL="http://{domain}"\n') if line.startswith('APP_URL=') else line for line in env_data]
        env_data = [line.replace('APP_DEBUG=', 'APP_DEBUG=false\n') if line.startswith('APP_DEBUG=') else line for line in env_data]

        with open(env_file_path, 'w') as file:
            file.writelines(env_data)

        if laravel_version > 10:
            self.setup_sqlite_database(env_file_path, site_path)

    def setup_sqlite_database(self, env_file_path, site_path):
        with open(env_file_path, 'r') as file:
            env_data = file.read()

        if 'DB_CONNECTION=sqlite' in env_data and '# DB_DATABASE' in env_data:
            about_info = run_command('php8.3 artisan about --only=drivers --json')
            about_data = json.loads(about_info)
            if about_data.get('database') == 'sqlite':
                sqlite_db_path = os.path.join(site_path, 'database', 'database.sqlite')
                open(sqlite_db_path, 'a').close()  # create the sqlite database file if it doesn't exist
                run_command('php8.3 artisan migrate --force')

    def run_migrations(self, site_path, nested_structure, nested_folder):
        if nested_structure:
            site_path = os.path.join(site_path, nested_folder)
        if os.path.isfile(os.path.join(site_path, 'artisan')):
            run_command(f'php8.3 {os.path.join(site_path, "artisan")} migrate --force')
