import concurrent.futures
import logging
import threading
from time import time


class TaskManager:
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

    def _cleanup_old_results(self):
        current_time = time()
        expired_keys = [key for key, (result, timestamp) in self.id_to_result.items() if
                        current_time - timestamp > 3600]
        for key in expired_keys:
            del self.id_to_result[key]

    def submit_task(self, func, *args, **kwargs):
        task_id = self._generate_unique_id()
        future = self.executor.submit(func, *args, **kwargs)
        logging.info(f"Future: {future}")
        self.future_to_id[future] = task_id
        logging.info(f"Task submitted with ID: {task_id}")
        future.add_done_callback(self._task_done_callback)
        return task_id

    def _task_done_callback(self, future):
        task_id = self.future_to_id.pop(future)
        try:
            result = future.result()
            self.id_to_result[task_id] = ({"task_id": task_id, "status": "completed", "result": result}, time())
        except Exception as e:
            self.id_to_result[task_id] = ({"task_id": task_id, "status": "error", "error": str(e)}, time())
        self._cleanup_old_results()

    def get_task_status(self, task_id):
        logging.info(f"Getting status for Task ID: {task_id}")
        logging.info(f"Tasks: {self.future_to_id}")
        if task_id in self.id_to_result:
            result, _ = self.id_to_result[task_id]
            return result
        for future, id in self.future_to_id.items():
            if id == task_id:
                if future.done():
                    try:
                        result = future.result()
                        return {"task_id": task_id, "status": "completed", "result": result}
                    except Exception as e:
                        return {"task_id": task_id, "status": "error", "error": str(e)}
                else:
                    return {"task_id": task_id, "status": "in_progress"}
        return {"message": "Task ID not found"}
