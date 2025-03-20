import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("My App")

#         self.label = QLabel() #라벨 정의

#         self.input = QLineEdit() #인풋
#         self.input.textChanged.connect(self.label.setText) #인풋 라벨로 전달달

#         layout = QVBoxLayout()
#         layout.addWidget(self.input)
#         layout.addWidget(self.label)

#         container = QWidget()
#         container.setLayout(layout)

#         self.setCentralWidget(container)

#마우스 이벤트
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Click in this window")
        self.setCentralWidget(self.label)

    def mouseMoveEvent(self, e):
        self.label.setText("드래그")

    def mousePressEvent(self, e):
        self.label.setText("클릭")

    def mouseReleaseEvent(self, e):
        self.label.setText("암것도.")

    def mouseDoubleClickEvent(self, e):
        self.label.setText("더블클릭")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()