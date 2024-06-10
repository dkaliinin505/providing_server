from flask import Blueprint, request, jsonify
from app.server_manager.actions.server_management_action import ServerManagementActions
from app.server_manager.actions.action2 import action2


server_manager_blueprint = Blueprint('server_manager', __name__)
