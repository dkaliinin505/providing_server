from utils.env_util import get_env_variable
from utils.util import run_command


def create_user(config: dict):
    db_root_password = get_env_variable('DB_ROOT_PASSWORD')
    db_user = config.get('db_user')
    db_user_password = config.get('db_user_password')
    db_host = config.get('db_host', '%')

    commands = [
        f"mysql --user='root' --password='{db_root_password}' -e \"DROP USER IF EXISTS '{db_user}'@'{db_host}';\"",
        f"mysql --user='root' --password='{db_root_password}' -e \"CREATE USER IF NOT EXISTS '{db_user}'@'{db_host}' IDENTIFIED WITH mysql_native_password BY '{db_user_password}';\"",
        f"mysql --user='root' --password='{db_root_password}' -e \"CREATE USER IF NOT EXISTS '{db_user}'@'%' IDENTIFIED WITH mysql_native_password BY '{db_user_password}';\""
    ]

    for command in commands:
        run_command(command)


def grant_privileges(config: dict):
    db_root_password = config.get('db_root_password')
    db_user = config.get('db_user')
    db_host = config.get('db_host', '%')
    db_privileges = config.get('db_privileges', [])

    for db_name in db_privileges:
        commands = [
            f"mysql --user='root' --password='{db_root_password}' -e \"GRANT ALL ON {db_name}.* TO '{db_user}'@'{db_host}' WITH GRANT OPTION;\"",
            f"mysql --user='root' --password='{db_root_password}' -e \"GRANT ALL ON {db_name}.* TO '{db_user}'@'%' WITH GRANT OPTION;\""
        ]

        for command in commands:
            run_command(command)

    run_command(f"mysql --user='root' --password='{db_root_password}' -e \"FLUSH PRIVILEGES;\"")
