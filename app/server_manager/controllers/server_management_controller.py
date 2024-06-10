from flask import jsonify
from app.server_manager.actions.server_management_action import ServerManagementActions
from app.server_manager.validators import validate_request
from app.server_manager.validators.schemas.validation_schema import RequestSchema, AnotherRequestSchema


class ServerManagementController:
    def __init__(self):
        self.services = ServerManagementActions()

    @validate_request({'POST': RequestSchema})
    def action1(self, data):
        result = self.services.action1(data)
        return jsonify(result)

    @validate_request({'POST': AnotherRequestSchema})
    def action2(self, data):
        result = self.services.action2(data)
        return jsonify(result)
