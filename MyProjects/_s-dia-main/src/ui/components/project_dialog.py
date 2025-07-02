from PySide6.QtWidgets import (QDialog, QMessageBox, QLineEdit, QTextEdit, 
                              QPushButton, QLabel, QVBoxLayout, QHBoxLayout)
from PySide6.QtCore import Qt
import os
import sys
import logging
import uuid
import json

from ..database import write_datasource
from src.ui.components.message_dialog import MessageDialog

class ProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        
        # 다이얼로그의 초기 크기 설정
        self.setMinimumSize(400, 300)
        self.resize(400, 300)

    def setup_ui(self):
        try:
            # 레이아웃 설정
            layout = QVBoxLayout()
            
            # 제목 레이블
            title_label = QLabel("프로젝트 생성")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #212529;
                    padding: 10px;
                }
            """)
            layout.addWidget(title_label)
            
            # 프로젝트명 입력
            name_layout = QHBoxLayout()
            name_label = QLabel("프로젝트명:")
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("프로젝트명을 입력하세요")
            name_layout.addWidget(name_label)
            name_layout.addWidget(self.name_input)
            layout.addLayout(name_layout)
            
            # 설명 입력
            desc_layout = QVBoxLayout()
            desc_label = QLabel("설명:")
            self.desc_input = QTextEdit()
            self.desc_input.setPlaceholderText("프로젝트에 대한 설명을 입력하세요")
            desc_layout.addWidget(desc_label)
            desc_layout.addWidget(self.desc_input)
            layout.addLayout(desc_layout)
            
            # 버튼 레이아웃
            button_layout = QHBoxLayout()
            self.save_button = QPushButton("저장")
            self.cancel_button = QPushButton("취소")
            
            # 버튼 스타일 설정
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #339af0;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #228be6;
                }
            """)
            
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #e9ecef;
                    color: #495057;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #dee2e6;
                }
            """)
            
            button_layout.addWidget(self.save_button)
            button_layout.addWidget(self.cancel_button)
            layout.addLayout(button_layout)
            
            # 시그널 연결
            self.save_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)
            
            self.setLayout(layout)
            
        except Exception as e:
            self.logger.error(f"프로젝트 생성 다이얼로그 UI 설정 중 오류 발생: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

    def get_project_data(self):
        """프로젝트 데이터를 반환합니다."""
        try:
            name = self.name_input.text().strip()
            description = self.desc_input.toPlainText().strip()
            
            if not name:
                QMessageBox.warning(self, "입력 오류", "프로젝트명을 입력하세요.")
                self.name_input.setFocus()
                return None
            
            return {
                'uuid': str(uuid.uuid4()),
                'name': name,
                'description': description,
                'created_at': None,  # 서버에서 설정
                'updated_at': None   # 서버에서 설정
            }
            
        except Exception as e:
            self.logger.error(f"프로젝트 데이터 생성 중 오류 발생: {str(e)}")
            return None

    def accept(self):
        """저장 버튼 클릭 시 처리"""
        try:
            project_data = self.get_project_data()
            if project_data is None:
                return
                
            # 프로젝트 디렉토리 생성
            if os.name == 'nt':  # Windows
                data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA', 'projects')
            else:  # Linux/Mac
                data_dir = os.path.expanduser('~/.upsdata/s-dia/projects')
            
            project_dir = os.path.join(data_dir, project_data['uuid'])
            os.makedirs(project_dir, exist_ok=True)
            
            # 프로젝트 정보 저장
            project_file = os.path.join(project_dir, 'project.json')
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            # 빈 데이터 소스 목록 파일 생성
            write_datasource(project_data['uuid'])
            
            super().accept()
            
        except Exception as e:
            self.logger.error(f"프로젝트 생성 중 오류 발생: {str(e)}")
            MessageDialog.critical(self, "오류", f"프로젝트 생성 중 오류가 발생했습니다.\n{str(e)}") 