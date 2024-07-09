from utils.async_util import run_command_async
from utils.env_util import async_get_env_variable


async def create_user(config):
    db_name = config.get('db_name')
    db_user = config.get('db_user')
    db_password = config.get('db_password')
    db_root_password = async_get_env_variable('DB_PASSWORD')

    create_user_command = f'mysql --user="root" --password="{db_root_password}" -e "CREATE USER \'{db_user}\'@\'%\' IDENTIFIED BY \'{db_password}\';"'
    await run_command_async(create_user_command)

    #grant_privileges_command = f'mysql --user="root" --password="{db_root_password}" -e "GRANT ALL PRIVILEGES ON `{db_name}`.* TO \'{db_user}\'@\'%\';"'
    #await run_command_async(grant_privileges_command)

    #flush_privileges_command = f'mysql --user="root" --password="{db_root_password}" -e "FLUSH PRIVILEGES;"'
    #await run_command_async(flush_privileges_command)


async def grant_privileges(config):
    db_name = config.get('db_name')
    db_user = config.get('db_user')
    db_privileges = config.get('db_privileges')
    db_root_password = async_get_env_variable('DB_PASSWORD')
    privileges_str = ', '.join(db_privileges)

    grant_privileges_command = f'mysql --user="root" --password="{db_root_password}" -e "GRANT {privileges_str} ON `{db_name}`.* TO \'{db_user}\'@\'%\';"'
    await run_command_async(grant_privileges_command)

    flush_privileges_command = f'mysql --user="root" --password="{db_root_password}" -e "FLUSH PRIVILEGES;"'
    await run_command_async(flush_privileges_command)
