import logging
import shutil
import traceback
from PySide6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QTextEdit, QPushButton
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QTextOption
from PySide6.QtUiTools import QUiLoader
import os

from common.deid import create_datasource, create_env, create_flow
from defined import DataType
from ui.common.file_utils import read_file
from ui.database import add_datasource, get_datasource_by_name, update_datasource
from ui.project_schema import Schema
from ups.run.flow import Flow
from utils.enum_utils import cnv_str_to_datatype, viewToDataType
# from ups.run.flow import Flow

logger = logging.getLogger(__name__)

class FlowProgressDialog(QDialog):
    """흐름 실행 진행률을 보여주는 다이얼로그"""
    
    # 취소 버튼 클릭 시그널
    canceled = Signal()
    process = None
    
    def __init__(self, flow_info, parent=None):
        super().__init__(parent)

        self.flow_info = flow_info

        flow_name = flow_info.get('name', '')
        
        # UI 파일 로드
        ui_file_path = os.path.join(os.path.dirname(__file__), "flow_progress_dialog.ui")
        loader = QUiLoader()
        self.ui = loader.load(ui_file_path)
        self.parent = parent

        self.datasource = self.parent.datasource
        # self.flow = parent.flow
        self.project = parent.project_data

        # 창 설정
        self.ui.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.ui.setFixedSize(600, 600)
        # self.ui.setWindowModality(Qt.WindowModal)

        self.ui.close_button.hide()
        
        # 타이틀 설정
        # self.ui.title_label.setText(f"{flow_name} 처리 중...")
        
        # 진행률 초기화
        self.ui.progress_bar.setValue(0)
        
        # 로그 텍스트 에디터 설정
        self.ui.log_textedit.setReadOnly(True)
        self.ui.log_textedit.setWordWrapMode(QTextOption.NoWrap)  # 워드랩 비활성화
        
        # 취소 버튼 연결
        self.ui.cancel_button.clicked.connect(self._on_cancel_clicked)
        self.ui.close_button.clicked.connect(self._on_close_clicked)
        
        # 취소 플래그
        self._is_canceled = False
        
        # 1초 후 run 메서드 호출하도록 타이머 설정
        QTimer.singleShot(1000, self.run)
    
    def _on_cancel_clicked(self):
        """취소 버튼 클릭 시 호출"""
        self._is_canceled = True
        self.canceled.emit()
        self.ui.close()
    
    def _on_close_clicked(self):
        """닫기 버튼 클릭 시 호출"""
        self.ui.close()
    
    def update_progress(self, value, log_message=None):
        """진행률과 로그 메시지 업데이트
        
        Args:
            value (int): 진행률 (0-100)
            log_message (str, optional): 추가할 로그 메시지
        """
        self.ui.progress_bar.setValue(value)
        if log_message:
            self.ui.log_textedit.append(log_message)
            # 스크롤을 항상 아래로
            self.ui.log_textedit.verticalScrollBar().setValue(
                self.ui.log_textedit.verticalScrollBar().maximum()
            )
    
    def write_log(self, log_message):
        """로그 메시지 추가"""
        self.ui.log_textedit.append(log_message)
        # 스크롤을 항상 아래로
        self.ui.log_textedit.verticalScrollBar().setValue(
            self.ui.log_textedit.verticalScrollBar().maximum()
        )

    def process_init(self, parent):
        """프로세스 초기화"""
        self.ui.progress_bar.setValue(0)
        self.ui.log_textedit.clear()
        self.ui.log_textedit.append("프로세스 초기화 중...")

        try:
            env, env_path = create_env(parent)
            flow, flow_path = create_flow(parent, env)

            if flow and flow.get('flow') and flow.get('flow').get('end') and flow.get('flow').get('end').get('parameters') and flow.get('flow').get('end').get('parameters').get('datasource') and flow.get('flow').get('end').get('parameters').get('datasource').get('path'):
                path = flow.get('flow').get('end').get('parameters').get('datasource').get('path')

                if os.path.exists(path):
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                    except PermissionError:
                        raise Exception(f"흐름 디렉토리 삭제 중 권한 오류가 발생했습니다.:\n     {path}")
                    except OSError as e:
                        raise Exception(f"흐름 디렉토리 삭제 중 오류가 발생했습니다: \n     {str(e)}")

            self.env = env
            self.flow = flow

            self.ui.log_textedit.append("프로세스 초기화 완료!")
            return [str(env_path), str(flow_path)]
        except Exception as e:
            # self.write_log(f"프로세스 초기화 중 오류 발생: {e}")
            # self.ui.progress_bar.setValue(100)
            self.ui.log_textedit.append(f"프로세스 초기화 중 오류가 발생했습니다.")
            self.ui.log_textedit.append(f"   {e}")
            logger.error(traceback.format_exc())
            self.ui.log_textedit.verticalScrollBar().setValue(
                self.ui.log_textedit.verticalScrollBar().maximum()
            )
            self.process_finish(success=True, err_msg=None)
        return None

    def callback(self, x):
        percent = x['current_schedule_completed_tasks'] / x['current_schedule_tasks'] * 100
        logger.info(f" {x['current_schedule_completed_tasks']} / {x['current_schedule_tasks']}   perse: {percent}%")
        self.update_progress(percent)

    def run(self):
        # try:
        ymls = self.process_init(self)
        if ymls:
            self.process_run(ymls)
            # else:
            #     self.process_finish(success=False, err_msg="프로세스 초기화 실패")
        # except Exception as e:
        #     self.write_log(f"흐름 실행 중 오류 발생: {str(e)}")
        #     self.process_finish(success=False, err_msg=str(e))
                
    def process_run(self, ymls):
        """프로세스 실행"""
        self.ui.close_button.hide()
        self.ui.cancel_button.show()

        self.ui.log_textedit.append("흐름 처리를 수행 합니다.")

        try:
            flow_process = Flow(ymls)
            flow_process.set_callback(self.callback)
            flow_process.run()
            self.process_finish(success=True, err_msg=None)
        except Exception as e:
            self.write_log(f"흐름 실행 중 오류가 발생 했습니다.")
            self.ui.log_textedit.append(f"   {e}")
            self.process_finish(success=False, err_msg=str(e))

        # except Exception as e:
        #     logger.error(traceback.format_exc())
        #     self.process_finish(success=False, err_msg=str(e))
    
        # 작업자 스레드 생성 및 시작
        # self.worker = FlowWorker(dlg, ymls)
        # self.worker.progress_updated.connect(self.update_progress)
        # self.worker.log_updated.connect(self.write_log)
        # self.worker.finished.connect(self.process_finish)
        # self.worker.start()


    def process_finish(self, success=True, err_msg=None):
        """프로세스 완료"""

        self.ui.close_button.show()
        self.ui.cancel_button.hide()

        if success:
            output_path = self.flow["flow"]["end"]["parameters"]["datasource"]["path"]
            file_schemas, first_rows = read_file(output_path, False, 0, "UTF-8", ",", 0)
            # cols = [ item.name for item in file_schemas ]
            schemas = []
            for schema in file_schemas:
                new_schema = {}

                new_schema['name'] = schema.name
                new_schema['comment'] = ''
                new_schema['data_type'] = cnv_str_to_datatype(schema.data_type.name).name
                new_schema['de_identi_attr'] = schema.de_identi_attr.name
                new_schema['is_distribution'] = schema.is_distribution
                new_schema['is_statistics'] = schema.is_statistics
                new_schema['exception_text'] = schema.exception_text
                new_schema['json'] = schema.json

                schemas.append(new_schema)

            # 기존 데이터 소스 확인
            ds = get_datasource_by_name(self.project.get('uuid', ''), self.flow_info.get('name'))
            
            new_ds = create_datasource(self.flow_info.get('name'), output_path, 'parquet', True, "UTF-8", ",", schemas)

            if ds:
                new_ds['uuid'] = ds['uuid']
                update_datasource(self.project.get('uuid', ''), new_ds)
            else:
                add_datasource(self.project.get('uuid', ''), new_ds)

            self.ui.progress_bar.setValue(100)
            self.ui.log_textedit.append("흐름 처리가 완료되었습니다.")

            self.parent.load_data_sources()
        # else:
            # self.ui.log_textedit.append("흐름 처리 중 오류가 발생했습니다.")
            # if err_msg:
            #     self.ui.log_textedit.append(f"   {err_msg}")
            
        self.ui.log_textedit.verticalScrollBar().setValue(
            self.ui.log_textedit.verticalScrollBar().maximum()
        )

    def is_canceled(self):
        """취소 여부 반환"""
        return self._is_canceled
    
    def exec(self):
        """다이얼로그 실행"""
        return self.ui.exec()
    
    def show(self):
        """다이얼로그 표시"""
        self.ui.show()
    
    def close(self):
        """다이얼로그 닫기"""
        self.ui.close() 