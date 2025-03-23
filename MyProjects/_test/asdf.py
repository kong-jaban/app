import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTextEdit, QVBoxLayout, QWidget

class FileProcessorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("파일 불러오기 및 가공")
        self.setGeometry(100, 100, 600, 400)

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 메뉴바에 "파일" 메뉴 추가
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("파일")
        
        open_action = file_menu.addAction("파일 열기")
        open_action.triggered.connect(self.open_file)

    def open_file(self):
        # 파일 다이얼로그 열기
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 열기", "", "텍스트 파일 (*.txt);;모든 파일 (*)")
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 파일 내용 가공: 소문자 변환, 줄별로 나누기
            processed_content = content.lower()
            lines = processed_content.splitlines()

            # 텍스트 박스에 가공된 내용 표시
            self.text_edit.clear()
            for line in lines:
                self.text_edit.append(line)

        except Exception as e:
            self.text_edit.setText(f"파일을 처리하는 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileProcessorWindow()
    window.show()
    sys.exit(app.exec())
