from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtUiTools import QUiLoader
from pathlib import Path
import os
import shutil
from typing import Optional, Dict, Any
import yaml
from common.deid import create_env
from ui.panels.flow_panel import ProcessCard

class Flow(QWidget):
    """플로우 위젯"""
    
    # 시그널 정의
    project_created = Signal(str)  # 프로젝트 생성 완료 시그널
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        """UI 초기화"""
        # 메인 레이아웃
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 타이틀
        self.title_label = QLabel("플로우")
        self.title_label.setStyleSheet("""
            QLabel {
                background-color: #4a90e2;
                color: white;
                padding: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
        """)
        layout.addWidget(self.title_label)
        
        # 컨트롤 영역
        self.control_widget = QWidget()
        control_layout = QVBoxLayout(self.control_widget)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(10)
        
        # 프로젝트 생성 버튼
        self.create_button = QPushButton("프로젝트 생성")
        control_layout.addWidget(self.create_button)
        
        # 프로세스 카드
        self.process_card = ProcessCard()
        self.process_card.hide()  # 초기에는 숨김
        control_layout.addWidget(self.process_card)
        
        layout.addWidget(self.control_widget)
        
    def _connect_signals(self):
        """시그널 연결"""
        self.create_button.clicked.connect(self._on_create_clicked)
        self.process_card.cancel_clicked.connect(self._on_cancel_clicked)
        
    def _on_create_clicked(self):
        """프로젝트 생성 버튼 클릭"""
        # 프로젝트 디렉토리 선택
        project_dir = QFileDialog.getExistingDirectory(
            self,
            "프로젝트 디렉토리 선택",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        
        if not project_dir:
            return
            
        # 프로젝트 생성 작업 시작
        self._start_project_creation(project_dir)
        
    def _start_project_creation(self, project_dir: str):
        """프로젝트 생성 작업 시작"""
        # UI 상태 변경
        self.create_button.setEnabled(False)
        self.process_card.show()
        self.process_card.set_title("프로젝트 생성 중...")
        self.process_card.set_progress(0)
        self.process_card.clear_log()
        self.process_card.set_cancel_enabled(True)
        
        # 작업 스레드 시작
        self.worker = ProjectCreationWorker(project_dir)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.log_updated.connect(self._on_log_updated)
        self.worker.finished.connect(self._on_creation_finished)
        self.worker.start()
        
    def _on_progress_updated(self, value: int):
        """진행률 업데이트"""
        self.process_card.set_progress(value)
        
    def _on_log_updated(self, message: str):
        """로그 업데이트"""
        self.process_card.add_log(message)
        
    def _on_creation_finished(self, success: bool, project_dir: str):
        """프로젝트 생성 완료"""
        # UI 상태 복원
        self.create_button.setEnabled(True)
        self.process_card.hide()
        
        if success:
            QMessageBox.information(self, "완료", "프로젝트가 생성되었습니다.")
            self.project_created.emit(project_dir)
        else:
            QMessageBox.critical(self, "오류", "프로젝트 생성 중 오류가 발생했습니다.")
            
    def _on_cancel_clicked(self):
        """취소 버튼 클릭"""
        if hasattr(self, 'worker'):
            self.worker.terminate()
            self.worker.wait()
            
        # UI 상태 복원
        self.create_button.setEnabled(True)
        self.process_card.hide()
        
class ProjectCreationWorker(QThread):
    """프로젝트 생성 작업 스레드"""
    
    # 시그널 정의
    progress_updated = Signal(int)  # 진행률 업데이트 시그널
    log_updated = Signal(str)  # 로그 업데이트 시그널
    finished = Signal(bool, str)  # 작업 완료 시그널 (성공 여부, 프로젝트 디렉토리)
    
    def __init__(self, project_dir: str):
        super().__init__()
        self.project_dir = project_dir
        
    def run(self):
        """작업 실행"""
        try:
            # 1. 프로젝트 디렉토리 생성
            self.log_updated.emit("프로젝트 디렉토리 생성 중...")
            os.makedirs(self.project_dir, exist_ok=True)
            self.progress_updated.emit(20)
            
            # 2. 데이터 디렉토리 생성
            self.log_updated.emit("데이터 디렉토리 생성 중...")
            data_dir = os.path.join(self.project_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
            self.progress_updated.emit(40)
            
            # 3. 설정 파일 생성
            self.log_updated.emit("설정 파일 생성 중...")
            create_env(self, self.project_dir)
            self.progress_updated.emit(60)
            
            # 4. UI 파일 복사
            self.log_updated.emit("UI 파일 복사 중...")
            ui_dir = os.path.join(self.project_dir, "ui")
            os.makedirs(ui_dir, exist_ok=True)
            
            # UI 파일 복사
            ui_files = [
                "project_panel.ui",
                "data_source_dialog.ui",
                "include/flow_left.ui"
            ]
            
            for ui_file in ui_files:
                src = os.path.join("src", "ui", ui_file)
                dst = os.path.join(ui_dir, ui_file)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                
            self.progress_updated.emit(80)
            
            # 5. 완료
            self.log_updated.emit("프로젝트 생성 완료!")
            self.progress_updated.emit(100)
            
            # 성공 신호 발생
            self.finished.emit(True, self.project_dir)
            
        except Exception as e:
            self.log_updated.emit(f"오류 발생: {str(e)}")
            # 실패 신호 발생
            self.finished.emit(False, self.project_dir) 