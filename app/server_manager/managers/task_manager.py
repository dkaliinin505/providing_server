import concurrent.futures
import logging
import threading
from time import time


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class TaskManager(metaclass=SingletonMeta):
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.future_to_id = {}
        self.id_to_result = {}
        self.id_counter = 0
        self.lock = threading.Lock()

    def _generate_unique_id(self):
        with self.lock:
            self.id_counter += 1
            return self.id_counter

    def submit_task(self, func, *args, **kwargs):
        task_id = self._generate_unique_id()
        future = self.executor.submit(func, *args, **kwargs)
        self.future_to_id[future] = task_id
        logging.info(f"Task submitted with ID: {task_id}")
        logging.info(f"Tasks: {self.future_to_id}")
        future.add_done_callback(self._task_done_callback)
        return task_id

    def _task_done_callback(self, future):
        task_id = self.future_to_id.pop(future)
        logging.info(f"Task completed with ID: {task_id}")
        try:
            result = future.result()
            self.id_to_result[task_id] = ({"task_id": task_id, "status": "completed", "result": result}, time())
        except Exception as e:
            self.id_to_result[task_id] = ({"task_id": task_id, "status": "error", "error": str(e)}, time())
        self.cleanup()

    def get_task_status(self, task_id):
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

    def cleanup(self):
        logging.info("Shutting down executor")
        self.executor.shutdown(wait=True)
        logging.info("Executor shut down")


