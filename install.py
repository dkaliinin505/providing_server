import os

from utils.util import run_command, module_exists, ensure_package_installed, user_exists, create_systemd_service, \
    check_service_exists, create_virtualenv, activate_virtualenv, install_requirements

# Ensure pip is installed
ensure_package_installed('pip')

# Ensure requests is installed
ensure_package_installed('requests')


def setup_server(server_id, sudo_password, db_password, callback, recipe_id):
    if os.geteuid() != 0:
        raise Exception("This script must be run as root.")

    uname = run_command("awk -F= '/^NAME/{print $2}' /etc/os-release | sed 's/\"//g'").strip()
    if uname != "Ubuntu":
        raise Exception("Forge only supports Ubuntu 20.04 and 22.04.")

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

    print('Installing Python packages')
    run_command("pip3 install httpie")
    run_command("pip3 install awscli awscli-plugin-endpoint")
    run_command("pip3 install Flask --ignore-installed")
    run_command("pip3 install marshmallow")
    run_command("pip3 install python-dotenv")

    print('Setting hostname, timezone, and sudo password')
    run_command('echo "bold-silence" > /etc/hostname')
    run_command(
        "sed -i 's/127\\.0\\.0\\.1.*localhost/127.0.0.1     bold-silence.localdomain bold-silence localhost/' /etc/hosts")
    run_command("hostname bold-silence")
    run_command("ln -sf /usr/share/zoneinfo/UTC /etc/localtime")
    password = run_command("mkpasswd -m sha-512 GMfEBKFCfPOTTWOfS7X3").strip()
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

    print("Creating systemd service")

    service_name = 'providingServer'
    current_directory = os.path.abspath(os.path.dirname(__file__))

    # Using current directory to find the script
    service_script_path = os.path.join(current_directory, "app/wsgi.py")
    print(f"Service script path: {service_script_path}")

    if not check_service_exists(service_name):
        create_systemd_service(service_name, service_script_path)
    else:
        print(f"Service {service_name} already exists.")



if __name__ == "__main__":
    env_name = "provoding_env"
    requirements_file = "requirements.txt"

    try:
        create_virtualenv(env_name)
        activate_virtualenv(env_name)
        install_requirements(requirements_file, env_name)
        setup_server(1, "123456", " ", " ", 1)
        print("Setup complete. The service is running.")
    except Exception as e:
        print(f"Installation failed: {e}")
