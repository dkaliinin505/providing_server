import os
import subprocess

from marshmallow import ValidationError


def count_installed_php_versions(self):
    try:
        result = subprocess.check_output(["ls", "/etc/php/"]).decode().strip().split("\n")
        if len(result) == 0:
            raise ValidationError("No PHP versions are installed")
        elif len(result) == 1:
            raise ValidationError("Only one PHP version is installed")
        return len(result)
    except subprocess.CalledProcessError:
        raise ValidationError("Cannot check installed PHP versions")
