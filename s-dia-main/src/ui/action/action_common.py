import copy
import os
import json
from PySide6.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QCheckBox, QHeaderView
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from src.ui.database import get_flow_by_uuid, update_flow, get_datasource
from src.ui.components.message_dialog import MessageDialog
from utils.enum_utils import sdataTypeToView

from ui.database import get_datasource


def validate_schema(parent, schemas, processes, flow_pos = -1):
    schema_list = copy.deepcopy(schemas)
    transformed_dict = {item["name"]: item for item in schema_list}
    schemas = [ item.get('name') for item in schema_list ]

    for proc_idx, process in enumerate(processes):
        if flow_pos != -1 and proc_idx >= flow_pos:
            break
        if process.get('process_type') == 'export':
            columns = [ col.get('column_name') for col in process.get('columns', []) if col.get('is_export') == True ]
            cols = []
            for idx, column in enumerate(schemas):
                if column in columns:
                    cols.append(column)
            schemas = cols
        elif process.get('process_type') == 'rename_columns':
            columns = [ col.get('column_name') for col in process.get('renames', []) ]
            cols = []
            for idx, column in enumerate(schemas):
                ren_cols = [col.get('new_column_name') for col in process.get('renames', []) if col.get("column_name") == column]
                if ren_cols:
                    cols.append(ren_cols[0])
                    transformed_dict[ren_cols[0]] = transformed_dict[column]
                    transformed_dict[ren_cols[0]]['name'] = ren_cols[0]
                    del transformed_dict[column]
                else:
                    cols.append(column)

            schemas = cols
        elif process.get('process_type') == 'union':
            target_datasource_uuid = process.get('target_datasource_uuid')
            # current_datasource_uuid = parent.current_data_source.get("uuid")
            right_datasource = get_datasource(parent.parent.project_data.get("uuid"), target_datasource_uuid)

            cols = []
            for right_schema in right_datasource.get('schemas', []):
                if right_schema.get('name') not in schemas:
                    transformed_dict[right_schema.get('name')] = right_schema
                    schemas.append(right_schema.get('name'))

    return schemas, transformed_dict

def select_saved_process_card(flow_panel, process_data, updated_flow, original_flow_pos=None):
    """
    저장 후 해당 프로세스 카드를 선택하는 공통 함수
    
    Args:
        flow_panel: FlowPanel 인스턴스
        process_data: 방금 저장한 프로세스 데이터
        updated_flow: 업데이트된 흐름 정보
        original_flow_pos: 원래 프로세스 위치 (편집 시 사용)
    """
    try:
        import logging
        print(f"카드 선택 시작 - process_type: {process_data.get('process_type')}, original_flow_pos: {original_flow_pos}")
        
        processes = updated_flow.get('processes', [])
        selected_index = -1
        
        # 가장 확실한 방법: original_flow_pos 사용
        if original_flow_pos is not None and original_flow_pos >= 0:
            # 편집인 경우: 원래 위치 사용
            if original_flow_pos < len(processes):
                selected_index = original_flow_pos
                logging.debug(f"편집 모드 - 원래 위치 사용: {selected_index}")
        else:
            # 신규 추가인 경우: 마지막 인덱스 사용
            selected_index = len(processes) - 1
            logging.debug(f"신규 추가 모드 - 마지막 위치 사용: {selected_index}")
        
        # 카드 선택 실행
        if selected_index != -1:
            logging.debug(f"카드 선택 실행 - 인덱스: {selected_index}")
            QTimer.singleShot(100, lambda: _select_process_card(flow_panel, selected_index))
        else:
            logging.warning(f"카드를 찾을 수 없음 - process_type: {process_data.get('process_type')}")
            
    except Exception as e:
        import logging
        logging.error(f"카드 선택 중 오류 발생: {str(e)}")

def _select_process_card(flow_panel, selected_index):
    """
    실제 카드 선택을 수행하는 내부 함수
    
    Args:
        flow_panel: FlowPanel 인스턴스
        selected_index: 선택할 카드의 인덱스
    """
    try:
        import logging
        if selected_index != -1 and selected_index < flow_panel.ui.process_list.count():
            item = flow_panel.ui.process_list.item(selected_index)
            flow_panel.ui.process_list.setCurrentItem(item)
            logging.debug(f"카드 선택 완료 - 인덱스: {selected_index}")
        else:
            logging.warning(f"카드 선택 실패 - 인덱스: {selected_index}, 총 카드 수: {flow_panel.ui.process_list.count()}")
    except Exception as e:
        import logging
        logging.error(f"카드 선택 실행 중 오류 발생: {str(e)}")
