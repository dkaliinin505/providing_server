from flask import jsonify

from app.server_manager.managers.task_manager import TaskManager


class Controller:

    def cleanup(self, resource_types=None):
        if resource_types is None:
            resource_types = []

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if any(isinstance(attr, resource_type) for resource_type in resource_types):
                delattr(self, attr_name)

    def __del__(self):
        self.cleanup()

    def __init__(self):
        self.task_manager = TaskManager()

    def get_task_status(self, task_id):
        status = self.task_manager.get_task_status(task_id)
        return jsonify(status)
