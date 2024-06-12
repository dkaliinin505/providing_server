from flask import Blueprint
from app.server_manager.services.server_management.server_management_service import ServerManagementService


server_manager_blueprint = Blueprint('server_manager', __name__)
