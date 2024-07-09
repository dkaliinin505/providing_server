from utils.async_util import run_command_async
from utils.env_util import async_get_env_variable


async def create_user(config):
    db_user = config.get('db_user')
    db_password = config.get('db_user_password')
    db_root_password = await async_get_env_variable('DB_PASSWORD')
    remote_ip = config.get('db_host')

    commands = [
        f'DROP USER IF EXISTS \'{db_user}\'@\'{remote_ip}\';',
        f'DROP USER IF EXISTS \'{db_user}\'@\'%\';',
        f'CREATE USER \'{db_user}\'@\'{remote_ip}\' IDENTIFIED BY \'{db_password}\';',
        f'CREATE USER \'{db_user}\'@\'%\' IDENTIFIED BY \'{db_password}\';'
    ]

    for command in commands:
        await run_command_async(f'mysql --user="root" --password="{db_root_password}" -e "{command}"')

    await run_command_async(f'mysql --user="root" --password="{db_root_password}" -e "FLUSH PRIVILEGES;"')


async def grant_privileges(config):
    db_name = config.get('db_name')
    db_user = config.get('db_user')
    db_privileges = config.get('db_privileges', ['SELECT'])
    db_root_password = await async_get_env_variable('DB_PASSWORD')
    db_host = config.get('db_host', '%')

    privileges_str = ', '.join(db_privileges)

    grant_privileges_command_ip = f'mysql --user="root" --password="{db_root_password}" -e "GRANT {privileges_str} ON `{db_name}`.* TO \'{db_user}\'@\'{db_host}\';"'
    await run_command_async(grant_privileges_command_ip)

    grant_privileges_command_wildcard = f'mysql --user="root" --password="{db_root_password}" -e "GRANT {privileges_str} ON `{db_name}`.* TO \'{db_user}\'@\'%\';"'
    await run_command_async(grant_privileges_command_wildcard)

    await run_command_async(f'mysql --user="root" --password="{db_root_password}" -e "FLUSH PRIVILEGES;"')
