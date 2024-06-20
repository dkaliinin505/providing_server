from flask import Flask
from app.server_manager.routes import server_manager_blueprint
from dotenv import load_dotenv


class App:
    def __init__(self):
        load_dotenv()
        self.app = Flask(__name__)
        self.app.register_blueprint(server_manager_blueprint)

    def run(self):
        self.app.run(host='0.0.0.0', port=5000)


app_instance = App()

if __name__ == "__main__":
    app_instance.run()
