import logging
import os
from quart import Quart
from app.server_manager.routes import server_manager_blueprint
from dotenv import load_dotenv
import asyncio


class App:
    def __init__(self):
        load_dotenv()
        self.app = Quart(__name__)
        self.app.register_blueprint(server_manager_blueprint)

    async def run(self):
        await self.app.run_task(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))


app_instance = App()


async def main():
    from app.server_manager.managers.task_manager import TaskManager
    task_manager = TaskManager()
    await task_manager.start_worker()
    await app_instance.run()


if __name__ == "__main__":
    asyncio.run(main())
