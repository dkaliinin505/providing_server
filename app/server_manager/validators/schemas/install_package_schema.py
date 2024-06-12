import os

from dotenv import load_dotenv
from marshmallow import Schema, fields, validate, ValidationError
from app.server_manager.validators.schemas.packages.mysql_config_schema import MysqlConfigSchema
from app.server_manager.validators.schemas.packages.nginx_config_schema import NginxConfigSchema
from app.server_manager.validators.schemas.packages.php_config_schema import PhpConfigSchema

load_dotenv()


class InstallPackageSchema(Schema):
    packages = os.getenv('ALLOWED_PACKAGES', 'php,nginx')
    package_name = fields.Str(required=True, validate=validate.OneOf(packages))
    config = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False)

    @staticmethod
    def load_config(package_name):
        if package_name == 'php':
            return PhpConfigSchema()
        elif package_name == 'nginx':
            return NginxConfigSchema()
        elif package_name == 'mysql':
            return MysqlConfigSchema()
        else:
            raise ValidationError({'package_name': 'Invalid package name'})
