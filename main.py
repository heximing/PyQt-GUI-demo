import sys
import traceback
from PyQt5.QtWidgets import QApplication
from PyQt_ex import MainWindow

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Error caught!!\n", tb)
    QApplication.quit()  # or QtWidgets.QApplication.exit(0)

if __name__ == "__main__":

    sys.excepthook = excepthook
    
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    window = MainWindow()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()

    # Your application won't reach here until you exit and the event
    # loop has stopped.

    print("End of '__main__'")
