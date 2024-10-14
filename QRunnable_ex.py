import sys
import time
import traceback
from PyQt5.QtCore import pyqtSignal, QRunnable, QThreadPool, QSize, QObject, pyqtSlot, QMutex
from PyQt5.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
    QApplication,
    QMainWindow,
    QPushButton,
)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    """
    progress = pyqtSignal(str)
    result = pyqtSignal(object)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)


class Worker(QRunnable):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.lock = getattr(kwargs, 'mutex', None)
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        if isinstance(self.lock, QMutex):  # if self.lock is not None:
            if self.lock.tryLock():
                self._running()
                self.lock.unlock()
            else:
                print("{}; {}.lock.tryLock() = False; skip...".format(__file__, self))
        else:
            self._running()

    def _running(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            print("{}; {}.Worker(QRunnable).run(); {} {}".format(time.ctime(), self, type(e), e))
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QtConcurrent demo")
        self.setMinimumSize(QSize(600, 300))

        _main_layout = QVBoxLayout()

        self.mutex = QMutex()  # only 1 (long-term) test can run at a time
        self.threadpool = QThreadPool()

        _concurrent = 3
        self.button = QPushButton("Start Worker(QRunnable)")
        self.button.clicked.connect(lambda s: self.start_thread(signal=s, con=_concurrent))
        _main_layout.addWidget(self.button)

        self.worker = []
        self.label = []
        self.result = []
        for i in range(_concurrent):
            self.label.append(QLabel("Label_{} Waiting for updates...".format(i)))
            _main_layout.addWidget(self.label[-1])
            self.result.append(QLabel("Result_{} Waiting for updates...".format(i)))
            _main_layout.addWidget(self.result[-1])
            _main_layout.addWidget(QLabel("---------------------------------------"))

        dummy_widget = QWidget()
        dummy_widget.setLayout(_main_layout)
        self.setCentralWidget(dummy_widget)

    def long_running_task(self, num, cycle: int = 9, **kwargs):
        print("{}; long_running_task(num = {} {}, cycle={})".format(time.ctime(), type(num), num, cycle))
        # Perform some time-consuming operation
        for i in range(cycle):
            if 'progress_callback' in kwargs:
                kwargs['progress_callback'].emit("Iteration {}".format(i))
                # FIXME: AttributeError: 'WorkerSignals' does not have a signal with the signature progress(QString)
            else:
                print("long_running_task(num = {} {}, cycle={}); Iteration {}".format(type(num), num, cycle, i))
            time.sleep(num + 0.5)

    def start_thread(self, signal, con: int):
        print("{}; start_thread(signal = {} {}, num={})".format(time.ctime(), type(signal), signal, con))
        if self.mutex.tryLock():
            for i in range(con):
                self.worker.append(Worker(self.long_running_task, i, 11))
                self.worker[-1].signals.progress.connect(lambda s, num=i: self.update_label(signal=s, num=num))
                self.worker[-1].signals.result.connect(lambda s, num=i: self.handle_result(signal=s, num=num))
                self.worker[-1].signals.finished.connect(
                    lambda num=i: print("{}; num = {}; Task finished.".format(time.ctime(), num)))
                self.threadpool.start(self.worker[-1])
            self.mutex.unlock()
        else:
            print("{}; {}.lock.tryLock() = False; skip...".format(__file__, self))

    def update_label(self, signal, num: int):
        # print("{}; update_label(signal = {} {}, num={})".format(time.ctime(), type(signal), signal, num))
        self.label[num].setText("{}; update_label(signal = {} {}, num={})".format(time.ctime(), type(signal), signal, num))

    def handle_result(self, signal, num: int):
        # print("{}; handle_result(signal = {} {}, num={})".format(time.ctime(), type(signal), signal, num))
        self.result[num].setText("{}; handle_result(signal = {} {}, num={})".format(time.ctime(), type(signal), signal, num))

    def _cleanup(self):
        # FIXME: RuntimeError: wrapped C/C++ object of type WorkerSignals has been deleted
        print("{}._cleanup() Successful.".format(self))


if __name__ == "__main__":
    def excepthook(exc_type, exc_value, exc_tb):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("{}; Error caught!!\n{}".format(time.ctime(), tb))
        QApplication.quit()  # or QtWidgets.QApplication.exit(0)

    sys.excepthook = excepthook

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
