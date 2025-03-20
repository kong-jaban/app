from PySide6.QtWidgets import QApplication, QMainWindow
from _ import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)


app = QApplication()
window = MainWindow()
window.show()
app.exec_()