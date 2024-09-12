import logging
import os
import shutil
import json
from pathlib import Path

import aiofiles.os

from app.server_manager.interfaces.command_interface import Command
from utils.env_util import async_get_env_variable, async_load_env, async_update_env_variable
from utils.async_util import run_command_async, check_file_exists, dir_exists
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DeployProjectCommand(Command):
    def __init__(self, config):
        self.config = config
        self.current_dir = Path(__file__).resolve().parent
        print(f"Config: {config}")

    async def execute(self, data):
        self.config = data
        domain = self.config.get('domain')
        repository_url = self.config.get('repository_url')
        branch = self.config.get('branch', 'master')
        ssh_command = f'ssh -F /home/super_forge/.ssh/{domain}-config'
        site_path = f'/home/super_forge/{domain}'
        is_nested_structure = self.config.get('is_nested_structure', False)
        nested_folder = self.config.get('nested_folder', 'app')

        logger.info(f"Removing site path: {site_path} if exists")

        # Remove the current site directory if it exists
        await run_command_async(f"rm -rf {site_path}", raise_exception=False)

        logger.info(f"Creating site path: {site_path}")

        try:
            await aiofiles.os.makedirs(site_path, exist_ok=True)
            logger.info(f"Successfully created site path: {site_path}")
        except Exception as e:
            logger.error(f"Failed to create site path: {site_path}, error: {str(e)}")
            raise

        # Before cloning the repository, check if the site already exists and running
        if is_nested_structure:
            env_file_path = os.path.join(site_path, nested_folder, '.env')
        else:
            env_file_path = os.path.join(site_path, '.env')
        logger.info(f"Checking env file path {env_file_path}")
        if await dir_exists(site_path):
            if await check_file_exists(env_file_path):
                # Load the .env file and check the APP_KEY
                app_key = await async_get_env_variable('APP_KEY', env_file_path)
                logger.info(f"APP_KEY: {app_key}")
                if app_key:
                    print(f"The site at {site_path} is already running with APP_KEY set.")
                    return {"message": "Site is already running."}

        # Remove The Current Site Directory if it exists
        if await dir_exists(site_path):
            shutil.rmtree(site_path)

        # Clone The Repository Into The Site
        await self.clone_repository(repository_url, branch, site_path, ssh_command, is_nested_structure, nested_folder)

        # Install Composer Dependencies If Requested
        await self.install_composer_dependencies(site_path, is_nested_structure, nested_folder)

        # Install NPM Dependencies If Requested
        await self.install_node_dependencies(site_path, is_nested_structure, nested_folder)

        # Create Environment File If Necessary
        await self.create_env_file(site_path, domain, is_nested_structure, nested_folder)

        # Run Artisan Migrations If Requested
        await self.run_migrations(site_path, is_nested_structure, nested_folder)

        # Run Artisan Commands after deployment
        await self.after_deployment(site_path, is_nested_structure, nested_folder)

        return {"message": "Site deployed and configured successfully"}

    async def check_database_exists(self, db_name, db_user, db_password):
        command = f'sudo mysql --user="{db_user}" --password="{db_password}" -e "CREATE DATABASE {db_name} CHARACTER SET utf8 COLLATE utf8_unicode_ci;"'
        logger.info(f"Checking if database {db_name} exists with command: {command}")
        try:
            await run_command_async(command, raise_exception=False)
            print(f"Database {db_name} exists.")
            return True
        except Exception as e:
            print(f"Database {db_name} does not exist: {str(e)}")
            return False

    async def clone_repository(self, repository_url, branch, site_path, ssh_command, is_nested_structure,
                               nested_folder):
        git_command = f'git clone --depth 1 --single-branch -c core.sshCommand="{ssh_command}" -b {branch} {repository_url} {site_path}'
        await run_command_async(git_command)
        os.chdir(site_path)
        await run_command_async(f'git config core.sshCommand "{ssh_command}"')
        await run_command_async('git submodule update --init --recursive')
        if is_nested_structure:
            nested_path = os.path.join(site_path, nested_folder)
            if not await dir_exists(nested_path):
                raise Exception(f"Nested path {nested_path} does not exist.")
            os.chdir(nested_path)

    async def install_composer_dependencies(self, site_path, is_nested_structure, nested_folder):
        if is_nested_structure:
            os.chdir(os.path.join(site_path, nested_folder))
        else:
            os.chdir(site_path)

        # Check if composer.lock file exists
        if await check_file_exists(os.path.join(site_path, 'composer.lock')):
            await run_command_async('rm -f composer.lock')

        await run_command_async(
            'php8.3 /usr/local/bin/composer install --no-interaction --prefer-dist --optimize-autoloader')

    async def create_env_file(self, site_path, domain, is_nested_structure, nested_folder):
        if is_nested_structure:
            site_path = os.path.join(site_path, nested_folder)

        laravel_version = self.get_laravel_version(site_path)
        env_file_path = os.path.join(site_path, '.env')

        if await check_file_exists(os.path.join(site_path, '.env.example')):
            shutil.copyfile(os.path.join(site_path, '.env.example'), env_file_path)
        else:
            env_content = self.generate_env_content(laravel_version)
            async with aiofiles.open(env_file_path, 'w') as env_file:
                await env_file.write(env_content)

        await self.update_env_file(env_file_path, laravel_version, domain, site_path)

    def get_laravel_version(self, site_path):
        composer_json_path = os.path.join(site_path, 'composer.json')
        with open(composer_json_path) as f:
            composer_data = json.load(f)
        laravel_version = composer_data.get('require', {}).get('laravel/framework', '0.0.0')
        laravel_version = laravel_version.lstrip('^')  # Remove the caret symbol if present
        return int(laravel_version.split('.')[0])

    def generate_env_content(self, laravel_version):
        template_directory = self.current_dir / '..' / '..' / '..' / 'templates' / 'laravel'
        if laravel_version >= 11:
            template_path = (template_directory / 'laravel_11_template.env').resolve()
        else:
            template_path = (template_directory / 'laravel_default_template.env').resolve()

        with open(template_path, 'r') as file:
            return file.read()

    async def update_env_file(self, env_file_path, laravel_version, domain, site_path):
        # Read the current .env file content
        async with aiofiles.open(env_file_path, 'r') as file:
            env_data = await file.readlines()

        # Create a dictionary to store the .env variables
        env_dict = {}
        for line in env_data:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                env_dict[key] = value

        # Update the specific values
        env_dict['APP_URL'] = f'http://{domain}'
        env_dict['APP_DEBUG'] = 'true'

        # Get the DB_PASSWORD from the main project .env file
        main_db_password = await async_get_env_variable('DB_PASSWORD')

        # Update the DB_PASSWORD in the cloned project .env file
        if main_db_password:
            print(f"Updating DB_PASSWORD: {main_db_password}")
            env_dict['DB_PASSWORD'] = main_db_password

        # Generate the updated .env content
        updated_env_data = '\n'.join([f'{key}={value}' for key, value in env_dict.items()])

        # Write the updated .env content back to the file
        async with aiofiles.open(env_file_path, 'w') as file:
            await file.write(updated_env_data)

        if laravel_version > 10:
            await self.setup_sqlite_database(env_file_path, site_path)

    async def setup_sqlite_database(self, env_file_path, site_path):
        async with aiofiles.open(env_file_path, 'r') as file:
            env_data = await file.read()

        if 'DB_CONNECTION=sqlite' in env_data and '# DB_DATABASE' in env_data:
            about_info = await run_command_async('php8.3 artisan about --only=drivers --json')
            about_data = json.loads(about_info)
            if about_data.get('database') == 'sqlite':
                sqlite_db_path = os.path.join(site_path, 'database', 'database.sqlite')
                open(sqlite_db_path, 'a').close()  # create the sqlite database file if it doesn't exist
                await run_command_async('php8.3 artisan migrate --force')

    async def run_migrations(self, site_path, is_nested_structure, nested_folder):
        if is_nested_structure:
            site_path = os.path.join(site_path, nested_folder)

        # Load DB credentials from .env
        dotenv_path = os.path.join(site_path, '.env')
        logger.info(f"Loading environment variables from {dotenv_path}")
        db_user = await async_get_env_variable('DB_USERNAME', dotenv_path)
        db_password = await async_get_env_variable('DB_PASSWORD', dotenv_path)
        db_name = await async_get_env_variable('DB_DATABASE', dotenv_path)
        db_host = await async_get_env_variable('DB_HOST', dotenv_path)

        print(f"Checking database {db_name} on host {db_host} with user {db_user}")
        logger.info(f"Checking database {db_name} on host {db_host} with user {db_user}")
        # Check if the database exists
        if not await self.check_database_exists(db_name, db_user, db_password):
            print(f"Database {db_name} does not exist. Creating the database.")
            if not await self.create_database_if_not_exists(db_name, db_user, db_password):
                print(f"Failed to create the database {db_name}.")
                return

        if await check_file_exists(os.path.join(site_path, 'artisan')):
            try:
                await run_command_async(f'php8.3 {os.path.join(site_path, "artisan")} migrate --force')
            except Exception as e:
                print(f"Error running migrations: {str(e)}")

    async def after_deployment(self, site_path, is_nested_structure, nested_folder):
        if is_nested_structure:
            site_path = os.path.join(site_path, nested_folder)

        # Grant privileges to the www-data user
        await run_command_async(f"sudo chown -R www-data:www-data {site_path}/storage")

        # Run additional commands after deployment
        try:
            await run_command_async(f"php8.3 {site_path}/artisan key:generate --force")
            await run_command_async(f"php8.3 {site_path}/artisan db:seed --force")
            await run_command_async(f"php8.3 {site_path}/artisan config:cache --force")
        except Exception as e:
            print(f"Error running after deployment commands: {str(e)}")
            logger.error(f"Error running after deployment commands: {str(e)}")

        return

    async def create_database_if_not_exists(self, db_name, db_user, db_password):
        create_db_command = f'sudo mysql --user="{db_user}" --password="{db_password}" -e "CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8 COLLATE utf8_unicode_ci;"'
        logger.info(f"Creating database {db_name} with command: {create_db_command}")
        try:
            await run_command_async(create_db_command)
            print(f"Database {db_name} created or already exists.")
        except Exception as e:
            print(f"Error creating database {db_name}: {str(e)}")
            return False
        return True

    async def install_node_dependencies(self, site_path, is_nested_structure, nested_folder):
        if is_nested_structure:
            os.chdir(os.path.join(site_path, nested_folder))
        else:
            os.chdir(site_path)
        if await check_file_exists(os.path.join(site_path, 'package.json')):
            await run_command_async('npm install')
