import os
from utils.util import run_command, module_exists, ensure_package_installed, user_exists, create_systemd_service, \
    check_service_exists, create_virtualenv, activate_virtualenv, install_requirements, install_python_venv


#
# # Ensure requests is installed
# ensure_package_installed('requests')


def setup_server(current_directory, env_name):
    if os.geteuid() != 0:
        raise Exception("This script must be run as root.")

    uname = run_command("awk -F= '/^NAME/{print $2}' /etc/os-release | sed 's/\"//g'").strip()
    if uname != "Ubuntu":
        raise Exception("Super Forge only supports Ubuntu 20.04 and 22.04.")

    if os.path.exists("/root/.superforge-provisioned"):
        raise Exception("This server has already been provisioned by Super Forge.")

    print('Starting to update server')
    if not os.path.exists("/root/.ssh"):
        os.makedirs("/root/.ssh")

    if not os.path.exists("/root/.ssh/authorized_keys"):
        open("/root/.ssh/authorized_keys", 'w').close()

    run_command("chown root:root /root")
    run_command("chown -R root:root /root/.ssh")
    run_command("chmod 700 /root/.ssh")
    run_command("chmod 600 /root/.ssh/authorized_keys")

    print('Adding new user')

    if not user_exists("super_forge"):
        run_command("useradd super_forge")

    os.makedirs("/home/super_forge/.ssh", exist_ok=True)
    os.makedirs("/home/super_forge/.forge", exist_ok=True)
    run_command("adduser super_forge sudo")
    run_command("chsh -s /bin/bash super_forge")
    run_command("cp /root/.profile /home/super_forge/.profile")
    run_command("cp /root/.bashrc /home/super_forge/.bashrc")

    print('Upgrade The Base Packages')
    os.environ['DEBIAN_FRONTEND'] = 'noninteractive'
    run_command("apt-get update")
    run_command("apt-get upgrade -y")

    print('Adding PPAs')
    run_command("apt-get install -y --force-yes software-properties-common")
    run_command("apt-add-repository ppa:ondrej/nginx -y")
    run_command("apt-add-repository ppa:ondrej/php -y")

    print('Adding Redis repository')
    distro_codename = run_command("lsb_release -cs").strip()
    run_command(
        f"curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg")
    run_command(
        f"echo 'deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb {distro_codename} main' | sudo tee /etc/apt/sources.list.d/redis.list")

    print('Updating Package Lists')
    run_command("apt-get update")
    run_command("add-apt-repository universe -y")
    run_command(
        "apt-get install -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold' -y --force-yes "
        "acl build-essential bsdmainutils cron curl fail2ban g++ gcc git jq libmagickwand-dev libmcrypt4 "
        "libpcre2-dev libpcre3-dev libpng-dev make ncdu net-tools pkg-config rsyslog "
        "sendmail sqlite3 supervisor ufw unzip uuid-runtime whois zip zsh")

    mkpasswd_installed = run_command("type mkpasswd").strip()
    if not mkpasswd_installed:
        raise Exception("Failed to install base dependencies.")

    print('Setting hostname, timezone, and sudo password')
    hostname = os.getenv('HOSTNAME', 'bold-silence')
    run_command(f'echo {hostname} > /etc/hostname')  # Env values
    run_command(
        f"sed -i 's/127\\.0\\.0\\.1.*localhost/127.0.0.1     {hostname}.localdomain {hostname} localhost/' /etc/hosts")  # Env values

    run_command(f"hostname {hostname}")
    run_command("ln -sf /usr/share/zoneinfo/UTC /etc/localtime")
    if not user_exists("super_forge"):
        sudo_password = os.getenv('SUDO_PASSWORD', 'GMfEBKFCfPOTTWOfS7X3')
        password = run_command(f"mkpasswd -m sha-512 {sudo_password} ").strip()  # GMfEBKFCfPOTTWOfS7X3
        run_command(f"usermod --password {password} super_forge")

    if not os.path.exists("/home/super_forge/.ssh"):
        os.makedirs("/home/super_forge/.ssh")

    if not os.path.exists("/home/super_forge/.ssh/id_rsa"):
        run_command("ssh-keygen -f /home/super_forge/.ssh/id_rsa -t rsa -N ''")

    print('Copying Source Control Public Keys into Known Hosts File')
    for host in ["github.com", "bitbucket.org", "gitlab.com"]:
        try:
            keys = run_command(f"ssh-keyscan -H {host}")
            print(f"Writing keys for {host}")
            with open("/home/super_forge/.ssh/known_hosts", "a") as known_hosts_file:
                known_hosts_file.write(keys)
        except Exception as e:
            print(f"Failed to scan keys for {host}: {e}")

    print('Configuring Git settings')
    run_command('git config --global user.name "Denis"')
    run_command('git config --global user.email "dp101196@gmail.com"')

    run_command('chown -R super_forge:super_forge /home/super_forge')
    run_command('chmod -R 755 /home/super_forge')
    run_command('chmod 700 /home/super_forge/.ssh/id_rsa')
    if not os.path.exists('/home/super_forge/.ssh/authorized_keys'):
        open('/home/super_forge/.ssh/authorized_keys', 'w').close()
    run_command('chmod 600 /home/super_forge/.ssh/authorized_keys')

    print('Setting up UFW Firewall')
    if module_exists("nf_conntrack"):
        run_command('ufw allow 22')
        run_command('ufw allow 80')
        run_command('ufw allow 443')
        run_command(f'ufw allow 5000')
        run_command('ufw --force enable')
    else:
        print("Module nf_conntrack not found. Skipping UFW setup.")

    print('Setting up sudoers for FPM, Nginx, and Supervisor')
    sudoers_content = [
        "super_forge ALL=NOPASSWD: /usr/sbin/service php8.3-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php8.2-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php8.1-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php8.0-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php7.4-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php7.3-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php7.2-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php7.1-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php7.0-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php5.6-fpm reload",
        "super_forge ALL=NOPASSWD: /usr/sbin/service php5-fpm reload"
    ]

    with open('/etc/sudoers.d/php-fpm', 'w') as f:
        f.write('\n'.join(sudoers_content) + '\n')

    nginx_content = [
        "super_forge ALL=NOPASSWD: /usr/sbin/service nginx *"
    ]
    with open('/etc/sudoers.d/nginx', 'w') as f:
        f.write('\n'.join(nginx_content) + '\n')

    supervisor_content = [
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl reload",
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl reread",
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl restart *",
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl start *",
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl status *",
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl status",
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl stop *",
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl update *",
        "super_forge ALL=NOPASSWD: /usr/bin/supervisorctl update"
    ]
    with open('/etc/sudoers.d/supervisor', 'w') as f:
        f.write('\n'.join(supervisor_content) + '\n')

    print("Creating provisioned file")
    open('/root/.superforge-provisioned', 'w').close()

    # Need to grant privileges for root directory for user super_forge
    print('current directory is:', current_directory)
    run_command(f'chown -R super_forge:super_forge {current_directory}')
    run_command(f'chmod -R 755 {current_directory}')

    sudoers_content = "super_forge ALL=(ALL) NOPASSWD:ALL\n"
    with open('/etc/sudoers.d/super_forge', 'w') as f:
        f.write(sudoers_content)
    run_command('chmod 440 /etc/sudoers.d/super_forge')

    print("Creating systemd service")

    service_name = 'providingServer'
    print('env_name:', env_name)

    # Using current directory to find the script
    service_script_path = os.path.join(current_directory, "app/wsgi.py")

    print(f"Service script path: {service_script_path}")

    if not check_service_exists(service_name):
        create_systemd_service(service_name, env_path, service_script_path)
    else:
        print(f"Service {service_name} already exists.")


if __name__ == "__main__":
    env_name = "providing_env"
    requirements_file = "requirements.txt"

    # Ensure pip is installed
    ensure_package_installed('pip')

    # Ensure python3-venv is installed
    install_python_venv()

    current_directory = os.path.abspath(os.path.dirname(__file__))
    env_path = os.path.join(current_directory, env_name)

    try:
        if not os.path.exists(env_name):
            # Create virtual environment
            create_virtualenv(env_name)
            activate_virtualenv(env_name)
            print("Virtual environment activated.")
            install_requirements(requirements_file, env_name)
            print("Virtual environment created")
            print(f"Please run the script again using following command to continue installation: {env_path}/bin/python install.py")
        else:
            from dotenv import load_dotenv

            load_dotenv()
            setup_server(current_directory, env_path)
            print("Setup complete. The service is running.")
    except Exception as e:
        print(f"Installation failed: {e}")
