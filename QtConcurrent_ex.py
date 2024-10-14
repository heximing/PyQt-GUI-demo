"""
PyQt5 doesn't directly expose the QtConcurrent namespace. However, you can achieve similar functionality using Python's built-in threading mechanisms or the concurrent.futures module.

Explanation:
Worker class:
This class encapsulates the execution of the task in a separate thread. It uses concurrent.futures.ThreadPoolExecutor to manage the thread pool.
Signals:
The finished signal is emitted when the task is completed, and the result signal is emitted with the result of the task.
run method:
This method starts the task in a separate thread.
on_complete method:
This method is called when the task is finished. It handles the result and emits signals.

Key Differences from QtConcurrent:
No direct mapping: PyQt5 doesn't provide a direct equivalent to QtConcurrent.
Pythonic approach: The example above uses Python's built-in threading mechanisms, which can be more familiar to Python developers.
Flexibility: You have more control over the execution of tasks and can easily integrate with other Python libraries.
"""


import sys
import traceback
import concurrent.futures
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow


class Worker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.func, *self.args, **self.kwargs)
            future.add_done_callback(self.on_complete)

    def on_complete(self, future):
        try:
            result = future.result()
            self.result.emit(result)
        except Exception as e:
            print("Error in worker thread: {}".format(e))
        finally:
            self.finished.emit()


if __name__ == "__main__":
    def excepthook(exc_type, exc_value, exc_tb):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("Error caught!!\n", tb)
        QApplication.quit()  # or QtWidgets.QApplication.exit(0)

    def long_running_task(arg1, arg2):
        # Perform some time-consuming operation
        return arg1 + arg2

    def handle_result(result):
        print("Result:", result)

    sys.excepthook = excepthook

    worker = Worker(long_running_task, 2, 3)
    worker.finished.connect(lambda: print("Task finished"))
    worker.result.connect(handle_result)
    worker.run()