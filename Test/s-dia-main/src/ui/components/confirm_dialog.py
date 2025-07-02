from PySide6.QtWidgets import QMessageBox

class ConfirmDialog(QMessageBox):
    """확인 메시지 박스 공통 컴포넌트"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("확인")
        self.setIcon(QMessageBox.Question)
        
        # 한글 버튼 추가
        self.yes_button = self.addButton("예", QMessageBox.YesRole)
        self.no_button = self.addButton("아니오", QMessageBox.NoRole)
        self.setDefaultButton(self.no_button)
    
    @classmethod
    def show(cls, parent, title, message):
        """확인 메시지 박스를 표시합니다.
        
        Args:
            parent: 부모 위젯
            title: 메시지 박스 제목
            message: 표시할 메시지
            
        Returns:
            bool: 사용자가 '예'를 선택한 경우 True, '아니오'를 선택한 경우 False
        """
        dialog = cls(parent)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.exec_()
        return dialog.clickedButton() == dialog.yes_button 