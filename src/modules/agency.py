import threading
import time
import uuid
from queue import Queue

class AgencyTask:
    def __init__(self, description, func, args=None, callback=None):
        self.id = str(uuid.uuid4())[:8]
        self.description = description
        self.func = func
        self.args = args or []
        self.callback = callback
        self.status = "PENDING"
        self.result = None
        self.created_at = time.time()

    def run(self):
        self.status = "RUNNING"
        try:
            print(f">> [Agency] Running Task {self.id}: {self.description}")
            if isinstance(self.args, dict):
                self.result = self.func(**self.args)
            else:
                self.result = self.func(*self.args)
            self.status = "COMPLETED"
        except Exception as e:
            self.status = "FAILED"
            self.result = str(e)
            print(f">> [Agency] Task {self.id} Failed: {e}")
        
        if self.callback:
            self.callback(self)

class Agency(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.task_queue = Queue()
        self.completed_tasks = []
        self.running = True
        print("Agency (Asynchronous Goal System) initialized.")

    def add_task(self, description, func, args=None, callback=None):
        task = AgencyTask(description, func, args, callback)
        self.task_queue.put(task)
        return task.id

    def run(self):
        while self.running:
            task = self.task_queue.get()
            if task is None: break
            
            task.run()
            self.completed_tasks.append(task)
            # Keep only last 20 tasks
            if len(self.completed_tasks) > 20:
                self.completed_tasks.pop(0)
            
            self.task_queue.task_done()

    def get_status_report(self):
        if not self.completed_tasks and self.task_queue.empty():
            return "No active or recent background tasks."
        
        report = "Background Task Report:\n"
        for t in self.completed_tasks:
            report += f"- [{t.status}] {t.description} (ID: {t.id})\n"
        
        if not self.task_queue.empty():
            report += f"- {self.task_queue.qsize()} tasks still in queue.\n"
        
        return report

# Global Agency Instance
cherry_agency = Agency()
cherry_agency.start()
