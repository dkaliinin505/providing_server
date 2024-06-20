import os
import shutil
import json
from dotenv import load_dotenv
from app.server_manager.interfaces.command_interface import Command
from utils.util import run_command
from utils.env_util import get_env_variable


class DeployProjectCommand(Command):
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
        is_nested_structure = self.config.get('is_nested_structure', False)
        nested_folder = self.config.get('nested_folder', 'app')

        # Ensure the parent directory exists
        os.makedirs(site_path, exist_ok=True)

        # Remove The Current Site Directory
        if os.path.exists(site_path):
            shutil.rmtree(site_path)

        # Clone The Repository Into The Site
        self.clone_repository(repository_url, branch, site_path, ssh_command, is_nested_structure, nested_folder)

        # Install Composer Dependencies If Requested
        self.install_composer_dependencies(site_path, is_nested_structure, nested_folder)

        # Create Environment File If Necessary
        self.create_env_file(site_path, domain, is_nested_structure, nested_folder)

        # Run Artisan Migrations If Requested
        self.run_migrations(site_path, is_nested_structure, nested_folder)

        # Run Artisan Commands after deployment
        self.after_deployment(site_path, is_nested_structure, nested_folder)

        return {"message": "Site deployed and configured successfully"}

    def check_database_exists(self, db_name, db_user, db_password, db_host='localhost'):
        command = f"mysql -u{db_user} -p{db_password} -h{db_host} -e 'USE {db_name};'"
        try:
            run_command(command, raise_exception=False)
            print(f"Database {db_name} exists.")
            return True
        except Exception as e:
            print(f"Database {db_name} does not exist: {str(e)}")
            return False

    def clone_repository(self, repository_url, branch, site_path, ssh_command, is_nested_structure, nested_folder):
        git_command = f'git clone --depth 1 --single-branch -c core.sshCommand="{ssh_command}" -b {branch} {repository_url} {site_path}'
        run_command(git_command)
        os.chdir(site_path)
        run_command(f'git config core.sshCommand "{ssh_command}"')
        run_command('git submodule update --init --recursive')
        if is_nested_structure:
            nested_path = os.path.join(site_path, nested_folder)
            if not os.path.exists(nested_path):
                raise Exception(f"Nested path {nested_path} does not exist.")
            os.chdir(nested_path)

    def install_composer_dependencies(self, site_path, is_nested_structure, nested_folder):
        if is_nested_structure:
            os.chdir(os.path.join(site_path, nested_folder))
        else:
            os.chdir(site_path)
        run_command('php8.3 /usr/local/bin/composer install --no-interaction --prefer-dist --optimize-autoloader')

    def create_env_file(self, site_path, domain, is_nested_structure, nested_folder):
        if is_nested_structure:
            site_path = os.path.join(site_path, nested_folder)
        laravel_version = self.get_laravel_version(site_path)
        env_file_path = os.path.join(site_path, '.env')

        if os.path.isfile(os.path.join(site_path, '.env.example')):
            shutil.copyfile(os.path.join(site_path, '.env.example'), env_file_path)
        else:
            env_content = self.generate_env_content(laravel_version)
            with open(env_file_path, 'w') as env_file:
                env_file.write(env_content)

        self.update_env_file(env_file_path, laravel_version, domain, site_path)

    def get_laravel_version(self, site_path):
        composer_json_path = os.path.join(site_path, 'composer.json')
        with open(composer_json_path) as f:
            composer_data = json.load(f)
        laravel_version = composer_data.get('require', {}).get('laravel/framework', '0.0.0')
        laravel_version = laravel_version.lstrip('^')  # Remove the caret symbol if present
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

    def update_env_file(self, env_file_path, laravel_version, domain, site_path):
        # Read the current .env file content
        with open(env_file_path, 'r') as file:
            env_data = file.readlines()

        # Create a dictionary to store the .env variables
        env_dict = {}
        for line in env_data:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                env_dict[key] = value

        # Update the specific values
        env_dict['APP_URL'] = f'http://{domain}'
        env_dict['APP_DEBUG'] = 'false'

        # Get the DB_PASSWORD from the main project .env file
        main_db_password = get_env_variable('DB_PASSWORD')

        # Update the DB_PASSWORD in the cloned project .env file
        if main_db_password:
            print(f"Updating DB_PASSWORD: {main_db_password}")
            env_dict['DB_PASSWORD'] = main_db_password

        # Generate the updated .env content
        updated_env_data = '\n'.join([f'{key}={value}' for key, value in env_dict.items()])

        # Write the updated .env content back to the file
        with open(env_file_path, 'w') as file:
            file.write(updated_env_data)

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

    def run_migrations(self, site_path, is_nested_structure, nested_folder):
        if is_nested_structure:
            site_path = os.path.join(site_path, nested_folder)

        # Load DB credentials from .env
        dotenv_path = os.path.join(site_path, '.env')
        load_dotenv(dotenv_path)
        db_user = get_env_variable('DB_USERNAME')
        db_password = get_env_variable('DB_PASSWORD')
        db_name = get_env_variable('DB_DATABASE')
        db_host = get_env_variable('DB_HOST', 'localhost')

        print(f"Checking database {db_name} on host {db_host} with user {db_user}")

        # Check if the database exists
        if not self.check_database_exists(db_name, db_user, db_password, db_host):
            print(f"Database {db_name} does not exist. Please create the database before running migrations.")
            return

        if os.path.isfile(os.path.join(site_path, 'artisan')):
            try:
                run_command(f'php8.3 {os.path.join(site_path, "artisan")} migrate --force')
            except Exception as e:
                print(f"Error running migrations: {str(e)}")

    def after_deployment(self, site_path, is_nested_structure, nested_folder):
        if is_nested_structure:
            site_path = os.path.join(site_path, nested_folder)

        # Run additional commands after deployment
        run_command(f"{site_path}/artisan config:cache")
        run_command(f"{site_path}/artisan key:generate")
        run_command(f"{site_path}/artisan db:seed")

        return
