import subprocess, json, os, sys, importlib
import venv


def run_command(command, return_json=False, raise_exception=True):
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, executable="/bin/bash")
    if result.returncode != 0:
        error_message = f"Command failed: {command}\n{result.stderr}"

        if return_json:
            return json.dumps({'error': error_message}), 400
        else:
            if raise_exception:
                raise Exception(error_message)
            else:
                print(error_message)
                return None
    print(f"Command output: {result.stdout}")
    return result.stdout.strip()


def install_package(package_name):
    print(f"Installing package: {package_name}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


def module_exists(module_name):
    result = subprocess.run(["modprobe", "-n", "-v", module_name], capture_output=True, text=True)
    return result.returncode == 0


def ensure_package_installed(package_name):
    try:
        importlib.import_module(package_name)
        print(f"{package_name} is already installed.")
    except ModuleNotFoundError:
        print(f"{package_name} not found. Installing {package_name}...")
        if package_name == 'pip':
            is_pip_installed = run_command(f"{sys.executable} -m ensurepip --upgrade", raise_exception=False)

            if is_pip_installed is None:
                run_command(f"sudo apt-get update")
                run_command(f"sudo apt-get install -y python3-pip")
        else:
            run_command(f"{sys.executable} -m pip install {package_name}", raise_exception=False)
            # Ensure the installed package is in sys.path
            user_base = subprocess.check_output([sys.executable, "-m", "site", "--user-base"]).decode().strip()
            user_site = os.path.join(user_base, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}',
                                     'site-packages')
            if user_site not in sys.path:
                sys.path.append(user_site)
            importlib.import_module(package_name)


def user_exists(username):
    try:
        run_command(f"id -u {username}")
        return True
    except Exception:
        return False


def create_systemd_service(service_name, env_path, script_path):
    service_file = f"/etc/systemd/system/{service_name}.service"
    with open(service_file, "w") as f:
        f.write(f"""
[Unit]
Description={service_name}
After=network.target

[Service]
User=super_forge
Group=super_forge
WorkingDirectory={os.path.abspath(os.path.dirname(__file__))}
ExecStart={env_path}/bin/python {script_path}
Restart=always

[Install]
WantedBy=multi-user.target
""")
    run_command("systemctl daemon-reload")
    run_command(f"systemctl enable {service_name}")
    run_command(f"systemctl start {service_name}")


def check_service_exists(service_name):
    result = subprocess.run(['systemctl', 'status', service_name], capture_output=True, text=True)
    if result.returncode != 0:
        return False
    return True


def provision_ping(server_id, status):
    url = "https://forge.laravel.com/provisioning/callback/status"
    data = {"status": status, "server_id": server_id}
    response = requests.post(url, data=data, verify=False)
    if response.status_code != 200:
        raise Exception(f"Failed to send status: {response.text}")


def install_python_venv():
    try:
        run_command("sudo apt-get update")
        run_command("sudo apt-get install -y python3-venv")
    except Exception as e:
        print(f"Failed to install python3-venv: {e}")
        raise


def create_virtualenv(env_name="providing_env"):
    if not os.path.exists(env_name):
        print(f"Creating virtual environment: {env_name}")
        try:
            venv.create(env_name, with_pip=True)
            print(f"Virtual environment {env_name} proceed. \n")
            if os.path.exists(env_name):
                print(f"Virtual environment {env_name} created successfully.")
            else:
                print(f"Failed to create virtual environment {env_name}.")
        except Exception as e:
            print(f"Failed to create virtual environment: {e}")
            print("Trying to install python3-venv and retry...")
            install_python_venv()
            try:
                venv.create(env_name, with_pip=True)
                if os.path.exists(env_name):
                    print(f"Virtual environment {env_name} created successfully after installing python3-venv.")
                else:
                    print(f"Failed to create virtual environment {env_name} after installing python3-venv.")
            except Exception as e:
                print(f"Failed to create virtual environment again: {e}")
                raise


def activate_virtualenv(env_name="providing_env"):
    activate_script = os.path.join(env_name, 'bin', 'activate')
    if not os.path.exists(activate_script):
        raise Exception(f"Activation script not found: {activate_script}")

    # Activate virtual environment
    print(f"Activating virtual environment: {activate_script}")
    command = f". {activate_script}"
    subprocess.run(command, shell=True, executable="/bin/bash")


def install_requirements(requirements_file, env_name="providing_env"):
    pip_path = os.path.join(env_name, 'bin', 'pip')
    run_command(f"{pip_path} install --upgrade setuptools wheel cython")
    run_command(f"{pip_path} install pyyaml")

    with open(requirements_file, 'r') as req_file:
        for line in req_file:
            package = line.strip()
            if package and not package.startswith('#'):
                try:
                    run_command(f"{pip_path} install {package}")
                except Exception as e:
                    print(f"Failed to install {package}: {e}")


def is_wsl():
    try:
        with open('/proc/version', 'r') as f:
            version_info = f.read()
        return 'Microsoft' in version_info or 'WSL' in version_info
    except FileNotFoundError:
        return False
