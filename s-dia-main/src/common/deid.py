import copy
import datetime
import json
import os
import uuid
import yaml
from pathlib import Path
from typing import Dict, Any
import time

from ui.database import get_datasource

# 템플릿 캐시
_env_template_cache: Dict[str, Any] = {}
_env_template_last_modified: float = 0
_flow_template_cache: Dict[str, Any] = {}
_flow_template_last_modified: float = 0

def _load_env_template() -> Dict[str, Any]:
    """env 템플릿 파일을 로드하고 캐시합니다.
    
    Returns:
        Dict[str, Any]: env 템플릿 설정
    """
    global _env_template_cache, _env_template_last_modified
    
    template_path = Path(__file__).parent.parent.parent / "templates" / "env_template.yml"
    current_mtime = template_path.stat().st_mtime
    
    # 템플릿이 변경되었거나 캐시가 없는 경우에만 다시 로드
    if current_mtime > _env_template_last_modified or not _env_template_cache:
        with open(template_path, "r", encoding="utf-8") as f:
            _env_template_cache = yaml.safe_load(f)
        _env_template_last_modified = current_mtime
    
    return _env_template_cache.copy()  # 캐시된 데이터의 복사본 반환

def _load_flow_template() -> Dict[str, Any]:
    global _flow_template_cache, _flow_template_last_modified

    template_path = Path(__file__).parent.parent.parent / "templates" / "flow_template.yml"
    current_mtime = template_path.stat().st_mtime

    if current_mtime > _flow_template_last_modified or not _flow_template_cache:
        with open(template_path, "r", encoding="utf-8") as f:
            _flow_template_cache = yaml.safe_load(f)
        _flow_template_last_modified = current_mtime
    
    return _flow_template_cache.copy()

def get_yml_datatype(data_type: str) -> str:
    """데이터 타입을 반환합니다.
    
    Args:
        data_type (str): 데이터 타입
    """
    if data_type == 'STRING':
        return 'string'
    elif data_type == 'INTEGER':
        return 'int'
    elif data_type == 'LONG':
        return 'long'
    elif data_type == 'DOUBLE':
        return 'double'
    elif data_type == 'DECIMAL':
        return 'decimal'
    elif data_type == 'FLOAT':
        return 'float'
    elif data_type == 'BOOLEAN':
        return 'boolean'
    elif data_type == 'DATETIME':
        return 'timestamp'
    elif data_type == 'DATE':
        return 'date'
    return data_type.lower()

def create_env(parent) -> tuple[dict, str]:
    """DEID 설정 파일을 생성합니다.
    
    Args:
        root_dir (str): 데이터 루트 디렉토리 경로
        log_name (str, optional): 로그 파일 이름. 기본값은 "s-dia"
        log_level (str, optional): 로그 레벨. 기본값은 "info"
    """
    # 템플릿 로드
    config = _load_env_template()
    
    datasource = parent.datasource
    flow = parent.flow_info
    project = parent.project
    
    # 파라미터로 전달된 값으로 덮어쓰기
    data_directory = project.get('data_directory', None)
    data_path = datasource.get('data_path', None)
    encoding = datasource.get('charset', 'utf-8')
    has_header = datasource.get('has_header', True)
    schemas = datasource.get('schemas', [])
    sep = datasource.get('separator', ',')
      
    if data_directory is None:
        raise ValueError("데이터 폴더가 등록되지 않았습니다.")

    if not os.path.exists(data_path):
        raise ValueError("데이터 파일이 존재하지 않습니다.")

    config["rootdir"] = os.path.join(data_directory, "02. 흐름", flow.get('name'))
    os.makedirs(config["rootdir"], exist_ok=True)

    is_csv = True if datasource.get('data_type', 'csv') == 'csv' else False

    config["log"]["file"] = f'{config["rootdir"]}/s-dia.log'

    if config.get("datasource_input") == None:
        config["datasource_input"] = {}

    if config.get("datasource_input").get('parameters') == None:
        config["datasource_input"]["parameters"] = {}

    if config.get("datasource_input").get('parameters').get('datasource') == None:
        config["datasource_input"]["parameters"]["datasource"] = {}

    config["datasource_input"]["parameters"]["datasource"]["schema"] = {}

    if is_csv:
        config["datasource_input"]["function"] = 'read_csv'
        config["datasource_input"]["parameters"]["datasource"]["type"] = 'csv'
        config["datasource_input"]["parameters"]["datasource"]["sep"] = sep
    else: # data_type == 'parquet':
        config["datasource_input"]["function"] = 'read_parquet'
        config["datasource_input"]["parameters"]["datasource"]["type"] = 'parquet'

    config["datasource_input"]["parameters"]["datasource"]["path"] = data_path
    config["datasource_input"]["parameters"]["datasource"]["encoding"] = encoding
    config["datasource_input"]["parameters"]["datasource"]["header"] = has_header


    for schema in schemas:
        col_name = schema.get('name', '')
        col_type = get_yml_datatype(schema.get('data_type', 'STRING'))
        config["datasource_input"]["parameters"]["datasource"]["schema"][col_name] = col_type

    # YAML 파일로 저장
    output_path = Path(config["rootdir"]) / "env.yml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return config, output_path
    
def convert_value(data_type: str, value: str):
    if data_type == 'STRING':
        return value
    elif data_type == 'INTEGER':
        return int(value)
    elif data_type == 'LONG':
        return int(value)
    elif data_type == 'DOUBLE':
        return float(value)
    elif data_type == 'DECIMAL':
        return float(value)
    elif data_type == 'FLOAT':
        return float(value)
    elif data_type == 'BOOLEAN':
        return bool(value)
    elif data_type == 'DATETIME':
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    elif data_type == 'DATE':
        return datetime.strptime(value, '%Y-%m-%d')

def create_flow(parent, env) -> tuple[dict, str]:
    config = _load_flow_template()

    datasource = parent.datasource
    flow_info = parent.flow_info
    project = parent.project
    
    # 파라미터로 전달된 값으로 덮어쓰기
    data_path = project.get('data_directory', None)

    config["rootdir"] = os.path.join(data_path, "02. 흐름", flow_info.get('name'))
    
    config["flow"]["start"] = env["datasource_input"]

    processes = flow_info.get('processes', [])
    config["flow"]["process"] = []

    schema_list = datasource.get("schemas", [])
    transformed_dict = {item["name"]: item for item in schema_list}
    schemas = [ item.get('name') for item in schema_list ]

    for idx, process in enumerate(processes):
        function = process.get('process_type', '')
        if function == 'export':
            proc = {}
            columns = [item.get('column_name') for item in process.get('columns') if item.get("is_export")]
            missing_columns = []
            for col in columns:
                if col not in schemas:
                    missing_columns.append(col)

            if missing_columns:
                raise ValueError(f"{idx+1}번째 처리에 다음 컬럼이 없습니다: {', '.join(missing_columns)}")

            schemas = columns

            proc["function"] = 'select_columns'
            proc["parameters"] = {}
            proc["parameters"]["columns"] = columns.copy()

            config["flow"]["process"].append(proc)
        elif function == 'drop_duplicates':
            columns = process.get('columns')
            missing_columns = []
            for col in columns:
                if col not in schemas:
                    missing_columns.append(col)

            if missing_columns:
                raise ValueError(f"{idx+1}번째 처리에 다음 컬럼이 없습니다: {', '.join(missing_columns)}")

            proc = {}
            proc["function"] = 'drop_duplicates'
            proc["parameters"] = {}
            proc["parameters"]["columns"] = process.get('columns')
            proc["parameters"]["keep"] = process.get('keep')
            proc["parameters"]["sort_order"] = {}

            for condition in process.get('sort_conditions', []):
                proc["parameters"]["sort_order"][condition.get('column')] = condition.get('order')

            config["flow"]["process"].append(proc)
        elif function == 'rename_columns':
            columns = process.get('renames')
            missing_columns = []
            renames = {}
            for obj_col in columns:
                if obj_col.get('column_name') not in schemas:
                    missing_columns.append(obj_col.get('column_name'))
                else:
                    renames[obj_col.get('column_name')] = obj_col.get('new_column_name')
                    index_of_bb = schemas.index(obj_col.get('column_name'))
                    schemas[index_of_bb] = obj_col.get('new_column_name')
                    transformed_dict[obj_col.get('new_column_name')] = copy.deepcopy(transformed_dict[obj_col.get('column_name')])

            if missing_columns:
                raise ValueError(f"{idx+1}번째 처리에 다음 컬럼이 없습니다: {', '.join(missing_columns)}")

            proc = {}
            proc["function"] = 'rename_columns'
            proc["parameters"] = {}
            proc["parameters"]["columns"] = renames
            
            config["flow"]["process"].append(proc)
            
        elif function == 'filter':
            filter_data = process.get('filter_data')
            connect_method = filter_data.get('connect_method', 'and')
            conditions = filter_data.get('conditions', [])

            proc = {}
            proc["function"] = 'filter'
            proc["parameters"] = {}
            proc["parameters"]["conditions"] = {}
            proc["parameters"]["conditions"][connect_method] = []

            missing_columns = []

            for condition in conditions:
                condi = {}
                condi["expression"] = {}
                column = condition.get('column', '')
                operator = condition.get('operator', '')
                value = condition.get('value', '')

                if column not in schemas:
                    missing_columns.append(column)
                else:
                    condi["expression"]['left'] = {}
                    condi["expression"]['left']['type'] = 'column'
                    condi["expression"]['left']['name'] = column
                    condi["expression"]['op'] = operator
                    condi["expression"]['right'] = convert_value(transformed_dict[column].get('data_type', 'STRING'), value)

                    proc["parameters"]["conditions"][connect_method].append(condi)

            config["flow"]["process"].append(proc)

            if missing_columns:
                raise ValueError(f"{idx+1}번째 처리에 다음 컬럼이 없습니다: {', '.join(missing_columns)}")

            config["flow"]["process"].append(proc)

        elif function == 'orderby':
            conditions = process.get('sort_conditions')
            na_position = process.get('na_position', 'last')
            # connect_method = filter_data.get('connect_method', 'and')
            # conditions = filter_data.get('sort_conditions', [])

            proc = {}
            proc["function"] = 'orderby'
            proc["parameters"] = {}
            proc["parameters"]["na_position"] = na_position
            proc["parameters"]["by"] = {}

            missing_columns = []

            for condition in conditions:
                column = condition.get('column', '')
                order = condition.get('order', '')

                if column not in schemas:
                    missing_columns.append(column)
                else:
                    proc["parameters"]["by"][column] = order


            if missing_columns:
                raise ValueError(f"{idx+1}번째 처리에 다음 컬럼이 없습니다: {', '.join(missing_columns)}")

            config["flow"]["process"].append(proc)

        elif function == 'union':
            # {
            #     "process_type": "union",
            #     "target_datasource_name": "흐름1_11",
            #     "target_datasource_uuid": "6dbe074e-f108-4e79-afc7-f037118531c5",
            #     "content": "테이블 행 결합: 흐름1_11"
            # }            
            target_datasource_uuid = process.get('target_datasource_uuid')
            right_datasource = get_datasource(project.get('uuid'), target_datasource_uuid)
            if right_datasource is None:
                raise ValueError(f"{idx+1}번째 처리에 다음 데이터 소스가 없습니다: {target_datasource_uuid}")
            right_schemas = right_datasource.get('schemas', [])

            data_type = right_datasource.get('data_type', '')
            charset = right_datasource.get('charset', '')
            separator = right_datasource.get('separator', '')
            datasource_path = right_datasource.get('data_path', '')
            has_header = right_datasource.get('has_header', True)
            proc = {}
            proc["function"] = 'union'
            proc["parameters"] = {}
            proc["parameters"]["right_ds"] = {}
            proc["parameters"]["right_ds"]["datasource"] = {}
            proc["parameters"]["right_ds"]["datasource"]["schema"] = {}
            for right_schema in right_schemas:
                col_name = right_schema.get('name', '')
                col_type = get_yml_datatype(right_schema.get('data_type', 'STRING'))

                if right_schema.get('name') not in schemas:
                    schemas.append(col_name)
                proc["parameters"]["right_ds"]["datasource"]["schema"][col_name] = col_type

            proc["parameters"]["right_ds"]["datasource"]["path"] = datasource_path
            proc["parameters"]["right_ds"]["datasource"]["sep"] = separator
            proc["parameters"]["right_ds"]["datasource"]["encoding"] = charset
            proc["parameters"]["right_ds"]["datasource"]["header"] = has_header
            proc["parameters"]["right_ds"]["datasource"]["type"] = data_type

            config["flow"]["process"].append(proc)

        elif function == 'join':
            target_datasource_uuid = process.get('target_datasource_uuid')
            right_datasource = get_datasource(project.get('uuid'), target_datasource_uuid)
            if right_datasource is None:
                raise ValueError(f"{idx+1}번째 처리에 다음 데이터 소스가 없습니다: {target_datasource_uuid}")
            right_schemas = right_datasource.get('schemas', [])

            join_left_columns = [ item.get('left_column') for item in process.get('join_columns', []) ]
            join_right_columns = [ item.get('right_column') for item in process.get('join_columns', []) ]

            data_type = right_datasource.get('data_type', '')
            charset = right_datasource.get('charset', '')
            separator = right_datasource.get('separator', '')
            datasource_path = right_datasource.get('data_path', '')
            has_header = right_datasource.get('has_header', True)
            proc = {}
            proc["function"] = 'join'
            proc["parameters"] = {}
            proc["parameters"]["right_ds"] = {}
            proc["parameters"]["right_ds"]["datasource"] = {}
            proc["parameters"]["right_ds"]["datasource"]["schema"] = {}
            for right_schema in right_schemas:
                col_name = right_schema.get('name', '')
                col_type = get_yml_datatype(right_schema.get('data_type', 'STRING'))

                if right_schema.get('name') not in schemas:
                    schemas.append(col_name)
                proc["parameters"]["right_ds"]["datasource"]["schema"][col_name] = col_type

            proc["parameters"]["right_ds"]["datasource"]["path"] = datasource_path
            proc["parameters"]["right_ds"]["datasource"]["sep"] = separator
            proc["parameters"]["right_ds"]["datasource"]["encoding"] = charset
            proc["parameters"]["right_ds"]["datasource"]["header"] = has_header
            proc["parameters"]["right_ds"]["datasource"]["type"] = data_type
            proc["parameters"]["how"] = process.get('join_type')
            proc["parameters"]["left_on"] = join_left_columns
            proc["parameters"]["right_on"] = join_right_columns
            proc["parameters"]["suffixes"] = ['_x', '_y']

            config["flow"]["process"].append(proc)

        elif function == 'rounding':
            decimal_places = process.get('decimal_places')
            columns = process.get('columns', [])

            proc = {}
            proc["function"] = 'round'
            proc["parameters"] = {}
            proc["parameters"]["columns"] = columns
            proc["parameters"]["decimals"] = decimal_places

            config["flow"]["process"].append(proc)


    config["flow"]["end"] = {}
    config["flow"]["end"]["function"] = 'write_parquet'
    config["flow"]["end"]["parameters"] = {}
    config["flow"]["end"]["parameters"]["datasource"] = {}
    config["flow"]["end"]["parameters"]["datasource"]["type"] = 'parquet'
    config["flow"]["end"]["parameters"]["datasource"]["path"] = os.path.join(config["rootdir"], f"{flow_info.get('name')}.parquet")

    output_path = Path(env["rootdir"]) / "flow.yml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return config, output_path

def create_datasource(flow_name, data_path, data_type, has_header, charset, separator, schemas):
    # 데이터 소스 생성
    datasource = {}

    datasource['name'] = flow_name

    if os.path.isdir(data_path):
        datasource['type'] = 'dir'
    else:
        datasource['type'] = 'file'

    datasource['data_type'] = data_type
    datasource['data_path'] = data_path
    datasource['charset'] = charset
    datasource['separator'] = separator
    datasource['has_header'] = has_header
    datasource['schemas'] = schemas

    return datasource



