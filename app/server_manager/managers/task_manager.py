import asyncio
import logging
from time import time

from utils.async_util import send_post_request_async
from utils.env_util import async_get_env_variable


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class TaskManager(metaclass=SingletonMeta):
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.future_to_id = {}
        self.id_to_result = {}
        self.id_counter = 0
        self.lock = asyncio.Lock()
        self.worker_count = 1

    async def _generate_unique_id(self):
        async with self.lock:
            self.id_counter += 1
            return self.id_counter

    async def submit_task(self, func, *args, **kwargs):
        task_id = await self._generate_unique_id()
        future = asyncio.get_event_loop().create_future()
        self.future_to_id[future] = task_id

        await self.task_queue.put((future, func, args, kwargs))
        logging.info(f"Task submitted with ID: {task_id}")
        logging.info(f"Tasks: {self.future_to_id}")

        return task_id

    async def worker(self):
        logging.info("Worker is running")
        while True:
            future, func, args, kwargs = await self.task_queue.get()
            task_id = self.future_to_id[future]
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                future.set_result(result)
                self.id_to_result[task_id] = ({"task_id": task_id, "status": "completed", "result": result}, time())
                logging.info(f"Task completed with ID: {task_id}")

                ip_address = await async_get_env_variable("IP_ADDRESS")
                # Send callback after task completion
                await send_post_request_async({
                    "task_id": task_id,
                    "ip_address": ip_address,
                    "status": "done"
                })

            except Exception as e:
                future.set_exception(e)
                self.id_to_result[task_id] = ({"task_id": task_id, "status": "error", "error": str(e)}, time())
                logging.error(f"Error for Task ID: {task_id}: {str(e)}")
            finally:
                self.task_queue.task_done()

    async def start_worker(self):
        for _ in range(self.worker_count):
            asyncio.create_task(self.worker())

    async def get_task_status(self, task_id):
        logging.info(f"Getting status for Task ID: {task_id}")
        logging.info(f"Tasks: {self.future_to_id}")
        logging.info(f"Results: {self.id_to_result}")
        logging.info("Trying to find task in Future")
        for future, future_id in self.future_to_id.items():
            if future_id == task_id:
                if future.done():
                    try:
                        result = future.result()
                        if asyncio.iscoroutine(result):
                            result = await result
                        self.id_to_result[task_id] = (
                            {"task_id": task_id, "status": "completed", "result": result}, time())
                        return {"task_id": task_id, "status": "completed", "result": result}
                    except Exception as e:
                        self.id_to_result[task_id] = (
                            {"task_id": task_id, "status": "error", "result": {"message": str(e)}}, time())
                        return {"task_id": task_id, "status": "error", "result": {"message": str(e)}}
                else:
                    return {"task_id": task_id, "status": "in_progress", "result": {"message": "Task in progress"}}
        return {"message": "Task ID not found"}
