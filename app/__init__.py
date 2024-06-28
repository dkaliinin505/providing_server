import logging
from flask import Flask
from app.server_manager.managers import task_manager
from app.server_manager.managers.task_manager import task_manager_instance
from app.server_manager.routes import server_manager_blueprint
from dotenv import load_dotenv


class App:
    def __init__(self):
        load_dotenv()
        self.app = Flask(__name__)
        self.app.register_blueprint(server_manager_blueprint)
        self.app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        logging.info("Application context teardown")
        task_manager_instance.cleanup()

    def run(self):
        self.app.run(host='0.0.0.0', port=5000)


app_instance = App()


if __name__ == "__main__":
    app_instance.run()
