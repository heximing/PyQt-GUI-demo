import sys
import traceback
from PyQt5.QtCore import QSize, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QApplication,
    QMainWindow,
)


class WorkerThread(QThread):
    update_label_signal = pyqtSignal(str)

    def run(self):
        for i in range(10):
            self.update_label_signal.emit(f"Iteration {i}")
            self.sleep(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QThread demo")
        self.setMinimumSize(QSize(400, 100))

        _main_layout = QVBoxLayout()

        self.label = QLabel("Waiting for updates...")

        _main_layout.addWidget(self.label)

        self.button = QPushButton("Start Thread")
        self.button.clicked.connect(self.start_thread)

        _main_layout.addWidget(self.button)

        self.worker = WorkerThread()
        self.worker.update_label_signal.connect(self.update_label)

        dummy_widget = QWidget()
        dummy_widget.setLayout(_main_layout)
        self.setCentralWidget(dummy_widget)

    def start_thread(self):
        self.worker.start()

    def update_label(self, text):
        self.label.setText(text)


if __name__ == '__main__':
    def excepthook(exc_type, exc_value, exc_tb):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print("Error caught!!\n", tb)
        QApplication.quit()  # or QtWidgets.QApplication.exit(0)

    sys.excepthook = excepthook

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())