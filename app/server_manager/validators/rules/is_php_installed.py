import os
import subprocess

from marshmallow import ValidationError


def php_v_installed(version):
    try:
        default_version = subprocess.check_output(['php', '-r', 'echo PHP_VERSION;']).decode().strip()
        return default_version.startswith(version)
    except subprocess.CalledProcessError:
        raise ValidationError("Cannot check if the PHP version is default")
