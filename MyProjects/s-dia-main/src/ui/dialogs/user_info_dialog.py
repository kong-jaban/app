from PySide6.QtWidgets import (QDialog, QWidget, QMessageBox, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, QApplication,
                              QFrame)
from PySide6.QtCore import Qt
import os
import json
import logging
from utils.crypto import CryptoUtil
from ..common.context_menu import CustomContextMenuFilter

class ModifiedLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._original_text = ""
        self._is_modified = False
        self.textChanged.connect(self._handle_text_change)

    def _handle_text_change(self, text):
        self._is_modified = text != self._original_text

    def setText(self, text):
        super().setText(text)
        self._original_text = text
        self._is_modified = False

    def isModified(self):
        return self._is_modified

class PasswordLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._password = ""
        self._is_modified = False
        self.textChanged.connect(self._handle_text_change)
        self.setEchoMode(QLineEdit.Password)

    def _handle_text_change(self, text):
        # 읽기 전용이거나 마스킹된 텍스트인 경우 무시
        if self.isReadOnly() or text == "*" * 10:
            return
        
        # 실제 입력이 있는 경우 비밀번호 업데이트
        if text != self._password:
            self._password = text
            self._is_modified = True
            super().setText(text)  # 실제 입력한 문자 수만큼 마스킹

    def text(self):
        return self._password

    def setText(self, text):
        self._password = text
        self._is_modified = False
        if self.echoMode() == QLineEdit.Password:
            super().setText("*" * 10)  # 항상 10개의 마스킹으로 시작
        else:
            super().setText(text)

    def getPassword(self):
        return self._password

    def isModified(self):
        return self._is_modified

    def setReadOnly(self, readonly):
        super().setReadOnly(readonly)
        # 읽기 전용으로 변경될 때는 항상 10개의 마스킹
        if readonly and self.echoMode() == QLineEdit.Password:
            super().setText("*" * 10)

class UserInfoDialog(QDialog):
    def __init__(self, user_info, parent=None):
        super().__init__(parent)
        self.user_info = user_info.copy()
        self.original_user_info = user_info.copy()
        self.edit_mode = False
        self.main_window = parent
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        
        # 컨텍스트 메뉴 필터 설정
        self.context_filter = CustomContextMenuFilter(self)
        
        # 모든 QLineEdit에 컨텍스트 메뉴 필터 적용
        for widget in self.findChildren(QLineEdit):
            widget.installEventFilter(self.context_filter)
        
    def setup_ui(self):
        self.setWindowTitle("사용자 정보")
        self.setMinimumWidth(600)  # 최소 너비만 설정
        self.setStyleSheet("""
            QDialog {
                background-color: #e9ecef;
            }
            QLabel {
                color: #000000;
                font-size: 14px;
                background-color: transparent;
            }
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #ffffff;
                font-size: 14px;
                min-height: 20px;
                color: #495057;
            }
            QLineEdit:focus {
                border: 1px solid #80bdff;
                outline: 0;
            }
            QLineEdit:read-only {
                background-color: #f8f9fa;
                border: 1px solid #ced4da;
            }
            QPushButton {
                color: #495057;
                background-color: #ffffff;
                border: 1px solid #ced4da;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
            QPushButton#edit_button {
                color: #fff;
                background-color: #007bff;
                border-color: #007bff;
                font-weight: bold;
            }
            QPushButton#edit_button:hover {
                color: #fff;
                background-color: #0069d9;
                border-color: #0062cc;
            }
            QPushButton#edit_button:pressed {
                background-color: #0062cc;
                border-color: #005cbf;
            }
            QFrame#form_container {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        
        # 메인 레이아웃
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 제목 컨테이너
        title_container = QWidget()
        title_container.setStyleSheet("background-color: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        # 제목 라벨
        title_label = QLabel("사용자 정보")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #000000;
            background-color: transparent;
        """)
        title_layout.addStretch(1)
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        
        self.main_layout.addWidget(title_container)
        
        # 입력 필드를 담을 컨테이너
        form_container = QFrame()
        form_container.setObjectName("form_container")
        form_container.setFrameShape(QFrame.StyledPanel)
        form_container.setFrameShadow(QFrame.Raised)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(4)
        
        # 사용자 ID
        id_text = QLabel("사용자 ID")
        id_required = QLabel("*")
        id_required.setStyleSheet("color: #dc3545; font-size: 16px; font-weight: bold;")
        id_text.setStyleSheet("font-size: 16px; font-weight: bold;")
        id_layout = QHBoxLayout()
        id_layout.setContentsMargins(0, 0, 0, 4)
        id_layout.setSpacing(2)
        id_layout.addWidget(id_text)
        id_layout.addWidget(id_required)
        id_layout.addStretch()
        form_layout.addLayout(id_layout)
        self.id_input = ModifiedLineEdit()
        self.id_input.setText(self.user_info['user_id'])
        self.id_input.setReadOnly(True)
        form_layout.addWidget(self.id_input)
        form_layout.addSpacing(16)
        
        # 사용자명
        name_text = QLabel("사용자명")
        name_required = QLabel("*")
        name_required.setStyleSheet("color: #dc3545; font-size: 16px; font-weight: bold;")
        name_text.setStyleSheet("font-size: 16px; font-weight: bold;")
        name_layout = QHBoxLayout()
        name_layout.setContentsMargins(0, 0, 0, 4)
        name_layout.setSpacing(2)
        name_layout.addWidget(name_text)
        name_layout.addWidget(name_required)
        name_layout.addStretch()
        form_layout.addLayout(name_layout)
        self.name_input = ModifiedLineEdit()
        self.name_input.setText(self.user_info['name'])
        self.name_input.setReadOnly(True)
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(16)
        
        # 비밀번호
        pw_text = QLabel("비밀번호")
        pw_required = QLabel("*")
        pw_required.setStyleSheet("color: #dc3545; font-size: 16px; font-weight: bold;")
        pw_text.setStyleSheet("font-size: 16px; font-weight: bold;")
        pw_layout = QHBoxLayout()
        pw_layout.setContentsMargins(0, 0, 0, 4)
        pw_layout.setSpacing(2)
        pw_layout.addWidget(pw_text)
        pw_layout.addWidget(pw_required)
        pw_layout.addStretch()
        form_layout.addLayout(pw_layout)
        self.pw_input = PasswordLineEdit()
        self.pw_input.setText(self.original_user_info['password'])
        self.pw_input.setReadOnly(True)
        form_layout.addWidget(self.pw_input)
        form_layout.addSpacing(16)
        
        # 비밀번호 확인
        pw_confirm_text = QLabel("비밀번호 확인")
        pw_confirm_required = QLabel("*")
        pw_confirm_required.setStyleSheet("color: #dc3545; font-size: 16px; font-weight: bold;")
        pw_confirm_text.setStyleSheet("font-size: 16px; font-weight: bold;")
        pw_confirm_layout = QHBoxLayout()
        pw_confirm_layout.setContentsMargins(0, 0, 0, 4)
        pw_confirm_layout.setSpacing(2)
        pw_confirm_layout.addWidget(pw_confirm_text)
        pw_confirm_layout.addWidget(pw_confirm_required)
        pw_confirm_layout.addStretch()
        form_layout.addLayout(pw_confirm_layout)
        
        self.pw_confirm_input = PasswordLineEdit()
        self.pw_confirm_input.setText(self.original_user_info['password'])
        self.pw_confirm_input.setReadOnly(True)
        self.pw_confirm_input.hide()
        form_layout.addWidget(self.pw_confirm_input)
        
        # 비밀번호 확인 라벨들 저장
        self.pw_confirm_text = pw_confirm_text
        self.pw_confirm_required = pw_confirm_required
        
        # 초기 상태에서는 비밀번호 확인 관련 위젯들 숨기기
        pw_confirm_text.hide()
        pw_confirm_required.hide()
        
        self.main_layout.addWidget(form_container)
        
        # 버튼
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.edit_button = QPushButton("수정")
        self.edit_button.setObjectName("edit_button")
        self.edit_button.setFixedWidth(120)
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        button_layout.addStretch(1)
        button_layout.addWidget(self.edit_button)
        
        self.main_layout.addLayout(button_layout)
        
        # 초기 크기 조정
        self.adjustSize()

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        
        # 수정 모드 전환
        if self.edit_mode:
            self.edit_button.setText("저장")
            self.id_input.setReadOnly(False)
            self.name_input.setReadOnly(False)
            self.pw_input.setReadOnly(False)
            self.pw_confirm_input.setReadOnly(False)
            self.pw_confirm_input.show()
            self.pw_confirm_text.show()
            self.pw_confirm_required.show()
            
            # 창 크기 자동 조정
            self.adjustSize()
        else:
            # 저장 처리
            if self.validate_and_save():
                # UI 상태를 보기 모드로 변경
                self.edit_button.setText("수정")
                self.id_input.setReadOnly(True)
                self.name_input.setReadOnly(True)
                self.pw_input.setReadOnly(True)
                self.pw_confirm_input.setReadOnly(True)
                self.pw_confirm_input.hide()
                self.pw_confirm_text.hide()
                self.pw_confirm_required.hide()
                
                # 메인 창의 사용자 정보 업데이트
                if self.main_window:
                    self.main_window.update_user_info(self.user_info)
                
                # 폼 컨테이너 크기 재조정
                QApplication.processEvents()
                self.adjustSize()
            else:
                self.edit_mode = True  # 유효성 검사 실패시 수정 모드 유지

    def validate_and_save(self):
        """입력값 검증 및 저장"""
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "경고", "사용자 ID를 입력하세요.")
            return False
            
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "경고", "사용자명을 입력하세요.")
            return False
            
        # 비밀번호 검증
        current_password = self.pw_input.getPassword().strip()
        confirm_password = self.pw_confirm_input.getPassword().strip()

        # 비밀번호와 비밀번호 확인이 다른 경우
        if current_password != confirm_password:
            QMessageBox.warning(self, "경고", "비밀번호가 일치하지 않습니다.")
            return False
            
        # 비밀번호가 비어있는 경우
        if not current_password:
            QMessageBox.warning(self, "경고", "비밀번호를 입력하세요.")
            return False
            
        try:
            # 새로운 사용자 정보 구성
            new_user_info = {
                "user_id": self.id_input.text().strip(),
                "name": self.name_input.text().strip(),
                "password": current_password,  # 검증된 비밀번호 사용
                "email": self.original_user_info.get('email', 'admin@upsdata.co.kr'),
                "role": self.original_user_info.get('role', 'admin'),
                "created_at": self.original_user_info.get('created_at', ''),
                "last_login": self.original_user_info.get('last_login', '')
            }
            
            # 파일 경로 설정
            if os.name == 'nt':  # Windows
                data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA')
            else:  # Linux/Mac
                data_dir = os.path.expanduser('~/.upsdata/s-dia')
            
            userinfo_path = os.path.join(data_dir, 'userinfo.json')
            
            # 암호화하여 저장
            crypto = CryptoUtil("S-DIA")
            crypto.save_encrypted_data(new_user_info, userinfo_path)
            
            # 성공적으로 저장되면 현재 정보 업데이트
            self.user_info = new_user_info.copy()
            self.original_user_info = new_user_info.copy()
            
            QMessageBox.information(self, "알림", "사용자 정보가 저장되었습니다.")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"사용자 정보 저장 중 오류가 발생했습니다.\n{str(e)}")
            return False 