from flask import Blueprint
from app.server_manager.controllers.server_management_controller import ServerManagementController

server_manager_blueprint = Blueprint('server_manager', __name__)
controller = ServerManagementController()


@server_manager_blueprint.route('/action1', methods=['POST'])
def action1_route():
    return controller.action1()


@server_manager_blueprint.route('/action2', methods=['POST'])
def action2_route():
    return controller.action2()
