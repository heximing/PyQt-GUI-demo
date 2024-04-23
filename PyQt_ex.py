import enum
import time
import sys
import traceback
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal, QRunnable, pyqtSlot, QObject, QThreadPool
from PyQt5.QtGui import QPalette, QColor, QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QStackedLayout,
    QTabWidget,
    QWidget,
    QMenu,
    QAction,
    QToolBar,
    QStatusBar,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
)


class Power(enum.Enum):
    OFF = 0
    ON = 1
    UNKNOWN = 2


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Pop-up Window!")

        q_btn = QDialogButtonBox.Apply | QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Close | QDialogButtonBox.Open | QDialogButtonBox.Help

        self.buttonBox = QDialogButtonBox(q_btn)
        # self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)
        # self.buttonBox.helpRequested.connect(lambda: self.done(int(2)))
        self.buttonBox.clicked.connect(self.handle_button_click)
        # !!! Attention !!! QDialogButtonBox signal is <class 'PyQt5.QtWidgets.QPushButton'> (QAbstractButton), not int

        self.layout = QVBoxLayout()
        message = QLabel("Something happened, is that OK?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def handle_button_click(self, clicked_button):
        """
        :param clicked_button:
        :return: <class 'int'> QDialog::DialogCode, which is QDialog::Accepted or QDialog::Rejected
        """
        button = self.buttonBox.standardButton(clicked_button)
        """
        role = self.buttonBox.buttonRole(clicked_button)
        print("handle_button_click().buttonRole(): ", type(role), role)
        if role == QDialogButtonBox.ApplyRole:
            print('ApplyRole Clicked')
        elif role == QDialogButtonBox.ResetRole:
            print('ResetRole Clicked')
        elif role == QDialogButtonBox.AcceptRole:
            print('AcceptRole Clicked')
        elif role == QDialogButtonBox.RejectRole:
            print('RejectRole Clicked')
        elif role == QDialogButtonBox.HelpRole:
            print('HelpRole Clicked')

        # QDialog::DialogCode only defines Accepted or Rejected, but it *can* be any int.
        self.setResult(button)
        print("QDialog.result() =", type(self.result()), self.result())
        """
        self.done(button)


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
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # self.show()

        self.setWindowTitle("GUI demo")
        self.setMinimumSize(QSize(400, 300))

        main_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        self.counter = 0
        self.timer = None
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_count)
        self.timer.start()
        self.label = QLabel("Start")
        main_layout.addWidget(self.label)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.btn_dict = {}
        btn = []
        """
        QAbstractButton provides four signals:
            pressed() is emitted when the left mouse button is pressed while the mouse cursor is inside the button.
            released() is emitted when the left mouse button is released.
            clicked() is emitted when the button is first pressed and then released, when the shortcut key is typed, or when click() or animateClick() is called.
            toggled() is emitted when the state of a toggle button changes.
        """
        for i, name in enumerate(["A", "B", "C", "D", "1", "2", "3", "4", "demo"]):
            btn.append(QPushButton(name))
            btn[i].setCheckable(True)
            btn[i].clicked.connect(lambda s, num=i, name_str=name: self.button_click(signal=s, btn_num=num, btn_name=name_str))
            btn_layout.addWidget(btn[i])
        main_layout.addLayout(btn_layout)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(True)
        for n, color in enumerate(["red", "green", "blue", "yellow"]):
            tabs.addTab(Color(color), color)
        main_layout.addWidget(tabs)

        dummy_widget = QWidget()
        dummy_widget.setLayout(main_layout)
        self.setCentralWidget(dummy_widget)

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # noqa: This is indeed correct, but PyCharm complains
        self.addToolBar(toolbar)

        # Some icons by Yusuke Kamiyamane. Licensed under a Creative Commons Attribution 3.0 License.
        button_action = QAction(QIcon("abacus.png"), "&Your Button", self)
        button_action.setStatusTip("This is your button")
        # TODO: .connect(lambda s: self.button_click(signal=s, btn_num=None, btn_name=None)) will cause error; why?
        button_action.toggled.connect(lambda s: self.tool_bar_click(signal=s))  # .triggered = .toggled
        button_action.setCheckable(True)
        # You can enter keyboard shortcuts using key names (e.g. Ctrl+p)
        # Qt.namespace identifiers (e.g. Qt.CTRL + Qt.Key_P)
        # or system agnostic identifiers (e.g. QKeySequence.Print)
        button_action.setShortcut(QKeySequence("Ctrl+p"))
        toolbar.addAction(button_action)

        button_action2 = QAction(QIcon("acorn.png"), "Your &Button2", self)
        button_action2.setStatusTip("This is your button2")
        button_action2.triggered.connect(self.tool_bar_click)
        button_action2.setCheckable(True)
        toolbar.addAction(button_action2)

        toolbar.addSeparator()

        button_action3 = QAction(QIcon("alarm-clock.png"), "Increase &Count", self)
        button_action3.setStatusTip("This is your button3")
        button_action3.triggered.connect(self.update_count)
        button_action3.setCheckable(False)
        toolbar.addAction(button_action3)

        toolbar.addSeparator()

        message_btn = QPushButton("QMessageBox")
        message_btn.setCheckable(True)
        message_btn.clicked.connect(self.q_message_box_clicked)
        message_btn.setStatusTip("Pop up a QMessageBox (a built-in message dialog class)")
        toolbar.addWidget(message_btn)

        toolbar.addSeparator()

        dialog_btn = QCheckBox("QDialog")
        dialog_btn.clicked.connect(self.dialog_clicked)
        dialog_btn.setStatusTip("Pop up a CustomDialog(QDialog)")
        toolbar.addWidget(dialog_btn)

        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)
        file_menu.addSeparator()
        file_submenu = file_menu.addMenu("&Submenu")
        file_submenu.addAction(button_action2)
        file_menu.addSeparator()

    def progress_fn(self, n):
        print("%d%% done" % n)

    def execute_this_fn(self, progress_callback):
        for n in range(0, 5):
            time.sleep(1)
            progress_callback.emit(int(n * 100 / 4))

        return "Done."

    def print_output(self, s):
        print("Result:", s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def oh_no(self):
        # Pass the function to execute
        worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)

    def update_count(self):
        self.counter += 1
        self.label.setText("Counter: %d" % self.counter)

    def tool_bar_click(self, signal):
        print("tool_bar_click(): Checked signal =", type(signal), signal)
    
    def button_click(self, signal: bool = None, btn_num: int = None, btn_name: str = None):
        power = Power.UNKNOWN
        if signal:
            power = Power.ON
        else:
            power = Power.OFF
        self.btn_dict["Power_" + btn_name] = power
        print("button_click(): Checked signal = {}, btn_num = {}, btn_name = '{}'".format(signal, btn_num, btn_name))
        print("self.btn_dict =", type(self.btn_dict), self.btn_dict)
        if btn_name == "demo":
            self.oh_no()

    def q_message_box_clicked(self, s):
        print("QMessageBox Checked:", s, end='; ')
        dlg = QMessageBox(self)
        dlg.setWindowTitle("I have a question!")
        dlg.setText("This is a simple dialog")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Ok | QMessageBox.Cancel | QMessageBox.Close | QMessageBox.Apply)
        dlg.setIcon(QMessageBox.Question)
        mes_box_dict = {QMessageBox.Ok: "Clicked 'OK'", QMessageBox.Cancel: "Clicked 'Cancel'",
                        QMessageBox.Close: "Clicked 'Close'", QMessageBox.Apply: "Clicked 'Apply'",
                        QMessageBox.Yes: "Clicked 'Yes'", QMessageBox.No: "Clicked 'No'", }
        """ !!! Attention !!!
        The result returned from QMessageBox is StandardButton enum, which is int.
        The result returned from Qdialog is QDialog::DialogCode, which is QDialog::Accepted or QDialog::Rejected;
            but QDialog::DialogCode is int, not bool, so it *can* be any number.
        """
        button = dlg.exec()
        print(type(button), button, "->" , mes_box_dict.get(button, None))

    def dialog_clicked(self, s):
        print("QDialog Checked:", s, end='; ')
        dlg = CustomDialog(parent=self)
        dlg.setMinimumSize(QSize(200, 100))
        """ !!! Attention !!!
        The result returned from QMessageBox is StandardButton enum, which is int.
        The result returned from Qdialog is QDialog::DialogCode, which is QDialog::Accepted or QDialog::Rejected;
            but QDialog::DialogCode is int, not bool, so it *can* be any number.
        """
        button = dlg.exec()
        print(type(button), button)

    """
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)
    
    def on_context_menu(self, pos):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(self.mapToGlobal(pos))

    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())
    """
