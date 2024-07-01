import asyncio
import logging
import threading
from time import time


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class TaskManager(metaclass=SingletonMeta):
    def __init__(self, max_workers=3):
        self.queue = asyncio.Queue()
        self.future_to_id = {}
        self.id_to_result = {}
        self.id_counter = 0
        self.lock = threading.Lock()
        self.max_workers = max_workers
        asyncio.create_task(self.worker())

    def _generate_unique_id(self):
        with self.lock:
            self.id_counter += 1
            return self.id_counter

    async def submit_task(self, func, *args, **kwargs):
        task_id = self._generate_unique_id()
        future = asyncio.get_event_loop().create_future()
        self.future_to_id[future] = task_id
        await self.queue.put((future, func, args, kwargs))
        logging.info(f"Task submitted with ID: {task_id}")
        logging.info(f"Tasks: {self.future_to_id}")
        return task_id

    async def worker(self):
        while True:
            future, func, args, kwargs = await self.queue.get()
            task_id = self.future_to_id[future]
            try:
                result = await func(*args, **kwargs)
                self.id_to_result[task_id] = ({"task_id": task_id, "status": "completed", "result": result}, time())
                future.set_result(result)
                logging.info(f"Task completed with ID: {task_id}")
            except Exception as e:
                self.id_to_result[task_id] = ({"task_id": task_id, "status": "error", "error": str(e)}, time())
                future.set_exception(e)
                logging.error(f"Error for Task ID: {task_id}: {str(e)}")
            self.queue.task_done()

    async def get_task_status(self, task_id):
        logging.info(f"Getting status for Task ID: {task_id}")
        logging.info(f"Tasks: {self.future_to_id}")
        logging.info(f"Results: {self.id_to_result}")

        if task_id in self.id_to_result:
            result, _ = self.id_to_result[task_id]
            return result

        for future, future_id in self.future_to_id.items():
            if future_id == task_id:
                if future.done():
                    try:
                        result = future.result()
                        self.id_to_result[task_id] = (
                            {"task_id": task_id, "status": "completed", "result": result}, time())
                        return {"task_id": task_id, "status": "completed", "result": result}
                    except Exception as e:
                        self.id_to_result[task_id] = ({"task_id": task_id, "status": "error", "error": str(e)}, time())
                        return {"task_id": task_id, "status": "error", "error": str(e)}
                else:
                    return {"task_id": task_id, "status": "in_progress"}
        return {"message": "Task ID not found"}
