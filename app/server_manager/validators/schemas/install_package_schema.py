import os

from dotenv import load_dotenv
from marshmallow import Schema, fields, validate, ValidationError
from app.server_manager.validators.schemas.packages.mysql_config_schema import MysqlConfigSchema
from app.server_manager.validators.schemas.packages.nginx_config_schema import NginxConfigSchema
from app.server_manager.validators.schemas.packages.php_config_schema import PhpConfigSchema
from app.server_manager.validators.schemas.packages.redis_config_schema import RedisConfigSchema

load_dotenv()


class InstallPackageSchema(Schema):
    packages = os.getenv('ALLOWED_PACKAGES', 'php,nginx')
    package_name = fields.Str(required=True, validate=validate.OneOf(packages))
    config = fields.Dict(keys=fields.Str(), values=fields.Raw(), required=False)

    @staticmethod
    def load_config(package_name):
        match package_name:
            case 'php':
                return PhpConfigSchema()
            case 'nginx':
                return NginxConfigSchema()
            case 'mysql':
                return MysqlConfigSchema()
            case 'redis':
                return RedisConfigSchema()
            case _:
                raise ValidationError({'package_name': 'Invalid package name'})
