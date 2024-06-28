import concurrent.futures
import logging
import threading


class TaskManager:
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.future_to_id = {}
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
        return task_id

    def get_task_status(self, task_id):
        logging.info(f"Task ID: {task_id}")
        logging.info(f"Tasks: {self.future_to_id}")
        for future, id in self.future_to_id.items():
            if id == task_id:
                if future.done():
                    try:
                        result = future.result()
                        return {"task_id": task_id, "status": "completed", "result": result}
                    except Exception as e:
                        logging.error(f"Error in task {task_id}: {str(e)}")
                        return {"task_id": task_id, "status": "error", "error": str(e)}
                else:
                    return {"task_id": task_id, "status": "in_progress"}
        return {"message": "Task ID not found"}
