import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

# QmainWindow를 상속 받아 앱의 Main Window를 커스텀
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("My App")

        self.button_is_checked = True
        self.button = QPushButton("Press Me!")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.the_button_was_clicked)
        # self.button.clicked.connect(self.the_button_was_toggled)
        self.button.setChecked(self.button_is_checked)
        #사이즈조절(최대,최소,고정값 등)
        self.setMinimumSize(400,300)
        # 윈도우 중앙에 위치할 Widget 설정
        self.setCentralWidget(self.button)


    def the_button_was_clicked(self):
        self.button.setText("You already clicked me.")
        self.button.setEnabled(False)
        self.setWindowTitle("My Oneshot App")

    def the_button_was_released(self):
        self.button_is_checked = self.button.isChecked()
        self.setWindowTitle("My Oneshot App")
        # print(self.button_is_checked)
app = QApplication(sys.argv)

window = MainWindow()
window.show()

# 이벤트 루프 시작 하기
app.exec_()

