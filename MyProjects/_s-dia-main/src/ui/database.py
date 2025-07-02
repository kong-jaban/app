import os
import json
import logging
import uuid
import shutil

# 메모리 내 캐시 역할을 할 딕셔너리
# { "project_uuid_1": [datasources...], "project_uuid_2": [datasources...] }
_datasource_cache = {}
_flow_cache = {}

logger = logging.getLogger(__name__)

def get_project_path(project_uuid):
    """프로젝트의 data 경로를 반환합니다."""
    if os.name == 'nt':  # Windows
        data_dir = os.path.join(os.getenv('LOCALAPPDATA', ''), 'UPSDATA', 'S-DIA', 'projects')
    else:  # Linux/Mac
        data_dir = os.path.expanduser('~/.upsdata/s-dia/projects')
    
    project_dir = os.path.join(data_dir, project_uuid)
    # 프로젝트 디렉토리가 없으면 생성
    os.makedirs(project_dir, exist_ok=True)

    return project_dir


def get_datasource_path(project_uuid):
    """프로젝트의 datasource.json 파일 경로를 반환합니다."""
    return os.path.join(get_project_path(project_uuid), 'datasource.json')


def get_datasources_list(project_uuid, force_reload=True):
    """
    데이터 소스 목록을 로드하고 반환합니다.
    메모리 캐시를 우선적으로 확인하고, 없으면 파일에서 로드합니다.
    force_reload=True 이면 캐시를 무시하고 파일에서 다시 로드합니다.
    """
    global _datasource_cache
    # 1. force_reload가 False일 때만 메모리 캐시를 확인
    if not force_reload and project_uuid in _datasource_cache:
        return _datasource_cache[project_uuid]

    # 2. 캐시를 무시하거나 캐시에 없을 때 파일에서 로드
    try:
        datasource_path = get_datasource_path(project_uuid)
        
        if os.path.exists(datasource_path):
            with open(datasource_path, 'r', encoding='utf-8') as f:
                try:
                    # 파일에서 읽어온 데이터를 캐시에 저장
                    loaded_data = json.load(f)
                    _datasource_cache[project_uuid] = loaded_data
                    return loaded_data
                except json.JSONDecodeError:
                    # 파일이 비어있거나 형식이 잘못된 경우
                    _datasource_cache[project_uuid] = []
                    return []
        else:
            # 파일이 존재하지 않는 경우
            _datasource_cache[project_uuid] = []
            return []

    except Exception as e:
        logger.error(f"데이터 소스 로드 중 오류 발생: {str(e)}")
        # 오류 발생 시에도 빈 리스트를 캐시하고 반환
        _datasource_cache[project_uuid] = []
        return []

def reload_datasources_from_file(project_uuid):
    """
    캐시를 무시하고 파일에서 데이터 소스 목록을 강제로 다시 로드합니다.
    """
    logger.info(f"'{project_uuid}' 프로젝트의 데이터소스를 파일에서 강제로 다시 로드합니다.")
    return get_datasources_list(project_uuid, force_reload=True)

def get_datasource(project_uuid, ds_uuid):
    """UUID로 특정 데이터 소스를 찾습니다."""
    data_sources = get_datasources_list(project_uuid)
    for ds in data_sources:
        if ds.get('uuid') == ds_uuid:
            return ds
    return None

def get_datasource_by_name(project_uuid, ds_name):
    """이름으로 특정 데이터 소스를 찾습니다."""
    data_sources = get_datasources_list(project_uuid)
    for ds in data_sources:
        if ds.get('name') == ds_name:
            return ds
    return None

def write_datasource(project_uuid):
    """
    메모리 캐시에 있는 현재 데이터 소스 목록을 파일에 저장(덮어쓰기)합니다.
    """
    global _datasource_cache
    # 저장할 데이터는 메모리 캐시에서 가져옵니다.
    data_to_write = _datasource_cache.get(project_uuid, [])
    
    try:
        datasource_path = get_datasource_path(project_uuid)
        
        # 안전한 저장을 위해 임시 파일 사용
        temp_file = datasource_path + ".tmp"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_write, f, ensure_ascii=False, indent=2)
        
        # 원자적 연산으로 파일 교체 (Windows에서도 잘 동작)
        os.replace(temp_file, datasource_path)
            
    except Exception as e:
        logger.error(f"데이터 소스 저장 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def add_datasource(project_uuid, data):
    """새 데이터 소스를 메모리와 파일에 추가합니다."""
    global _datasource_cache
    try:
        # 1. 현재 목록을 메모리(캐시)에서 가져옵니다.
        data_sources = get_datasources_list(project_uuid)
        
        # 2. 새 데이터를 메모리에 추가합니다.
        data['uuid'] = str(uuid.uuid4())
        data_sources.append(data)
        
        # 3. 변경된 메모리 내용을 파일에 씁니다.
        write_datasource(project_uuid)
    except Exception as e:
        logger.error(f"데이터 소스 추가 중 오류 발생: {str(e)}")

def update_datasource(project_uuid, data):
    """데이터 소스를 메모리와 파일에서 업데이트합니다."""
    global _datasource_cache
    # 1. 현재 목록을 메모리(캐시)에서 가져옵니다.
    data_sources = get_datasources_list(project_uuid)
    
    # 2. 메모리에서 해당 데이터를 찾아 업데이트합니다.
    for i, ds in enumerate(data_sources):
        if ds.get('uuid') == data.get('uuid'):
            data_sources[i] = data
            break
            
    # 3. 변경된 메모리 내용을 파일에 씁니다.
    write_datasource(project_uuid)

def delete_datasource(project_uuid, ds_uuid):
    """데이터 소스를 메모리와 파일에서 삭제합니다."""
    global _datasource_cache
    # 1. 현재 목록을 메모리(캐시)에서 가져옵니다.
    data_sources = get_datasources_list(project_uuid)
    
    # 2. 메모리에서 해당 데이터를 찾아 삭제합니다.
    # 리스트 순회 중 삭제는 위험하므로, 새로운 리스트를 만드는 것이 안전합니다.
    _datasource_cache[project_uuid] = [ds for ds in data_sources if ds.get('uuid') != ds_uuid]
    
    # 3. 변경된 메모리 내용을 파일에 씁니다.
    write_datasource(project_uuid)
    

def get_flow_path(project_uuid):
    """프로젝트의 flow.json 파일 경로를 반환합니다."""
    return os.path.join(get_project_path(project_uuid), 'flow.json')

def get_flow_list(project_uuid, force_reload=True):
    """
    흐름 목록을 로드하고 반환합니다.
    메모리 캐시를 우선적으로 확인하고, 없으면 파일에서 로드합니다.
    force_reload=True 이면 캐시를 무시하고 파일에서 다시 로드합니다.
    """
    global _flow_cache
    # 1. force_reload가 False일 때만 메모리 캐시를 확인
    if not force_reload and project_uuid in _flow_cache:
        return _flow_cache[project_uuid]

    # 2. 캐시를 무시하거나 캐시에 없을 때 파일에서 로드
    try:
        flow_path = get_flow_path(project_uuid)
        
        if os.path.exists(flow_path):
            with open(flow_path, 'r', encoding='utf-8') as f:
                try:
                    # 파일에서 읽어온 데이터를 캐시에 저장
                    loaded_data = json.load(f)
                    _flow_cache[project_uuid] = loaded_data
                    return loaded_data
                except json.JSONDecodeError:
                    # 파일이 비어있거나 형식이 잘못된 경우
                    _flow_cache[project_uuid] = []
                    return []
        else:
            # 파일이 존재하지 않는 경우
            _flow_cache[project_uuid] = []
            return []

    except Exception as e:
        logger.error(f"흐름 로드 중 오류 발생: {str(e)}")
        # 오류 발생 시에도 빈 리스트를 캐시하고 반환
        _flow_cache[project_uuid] = []
        return []

def reload_flow_from_file(project_uuid):
    """
    캐시를 무시하고 파일에서 흐름 목록을 강제로 다시 로드합니다.
    """
    logger.info(f"'{project_uuid}' 프로젝트의 흐름을 파일에서 강제로 다시 로드합니다.")
    return get_flow_list(project_uuid, force_reload=True)

def get_flow_by_uuid(project_uuid, flow_uuid):
    """UUID로 특정 흐름을 찾습니다."""
    flows = get_flow_list(project_uuid)
    for flow in flows:
        if flow.get('uuid') == flow_uuid:
            return flow
    return None

def get_flow_by_name(project_uuid, flow_uuid):
    """이름으로 특정 데이터 소스를 찾습니다."""
    flows = get_flow_list(project_uuid)
    for flow in flows:
        if flow.get('name') == flow_uuid:
            return flow
    return None

def write_flow(project_uuid):
    """
    메모리 캐시에 있는 현재 흐름 목록을 파일에 저장(덮어쓰기)합니다.
    """
    global _flow_cache
    # 저장할 데이터는 메모리 캐시에서 가져옵니다.
    data_to_write = _flow_cache.get(project_uuid, [])
    
    try:
        flow_path = get_flow_path(project_uuid)
        
        # 안전한 저장을 위해 임시 파일 사용
        temp_file = flow_path + ".tmp"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_write, f, ensure_ascii=False, indent=2)
        
        # 원자적 연산으로 파일 교체 (Windows에서도 잘 동작)
        os.replace(temp_file, flow_path)
            
    except Exception as e:
        logger.error(f"데이터 소스 저장 중 오류 발생: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

def add_flow(project_uuid, data):
    """새 흐름을 메모리와 파일에 추가합니다."""
    global _flow_cache
    try:
        # 1. 현재 목록을 메모리(캐시)에서 가져옵니다.
        flows = get_flow_list(project_uuid)
        
        # 2. 새 데이터를 메모리에 추가합니다.
        data['uuid'] = str(uuid.uuid4())
        flows.append(data)
        
        # 3. 변경된 메모리 내용을 파일에 씁니다.
        write_flow(project_uuid)
    except Exception as e:
        logger.error(f"흐름 추가 중 오류 발생: {str(e)}")

def update_flow(project_uuid, data):
    """흐름을 메모리와 파일에서 업데이트합니다."""
    global _flow_cache
    # 1. 현재 목록을 메모리(캐시)에서 가져옵니다.
    flows = get_flow_list(project_uuid)
    
    # 2. 메모리에서 해당 데이터를 찾아 업데이트합니다.
    for i, ds in enumerate(flows):
        if ds.get('uuid') == data.get('uuid'):
            flows[i].update(data)
            
            break
            
    # 3. 변경된 메모리 내용을 파일에 씁니다.
    write_flow(project_uuid)

def delete_flow(project_uuid, flow_uuid):
    """흐름을 메모리와 파일에서 삭제합니다."""
    global _flow_cache
    try:
        # 1. 현재 목록을 메모리(캐시)에서 가져옵니다.
        flows = get_flow_list(project_uuid)
        
        # 2. 메모리에서 해당 데이터를 찾아 삭제합니다.
        # 리스트 순회 중 삭제는 위험하므로, 새로운 리스트를 만드는 것이 안전합니다.
        _flow_cache[project_uuid] = [flow for flow in flows if flow.get('uuid') != flow_uuid]
        
        # 3. 변경된 메모리 내용을 파일에 씁니다.
        write_flow(project_uuid)

        # 4. 흐름 디렉토리 삭제
        flow_dir = os.path.join(get_project_path(project_uuid), "02. 흐름", flow_uuid)
        if os.path.exists(flow_dir):
            try:
                shutil.rmtree(flow_dir)
            except PermissionError:
                logger.error(f"흐름 디렉토리 삭제 중 권한 오류 발생: {flow_dir}")
                raise Exception("흐름 디렉토리 삭제 중 권한 오류가 발생했습니다.")
            except OSError as e:
                logger.error(f"흐름 디렉토리 삭제 중 오류 발생: {str(e)}")
                raise Exception(f"흐름 디렉토리 삭제 중 오류가 발생했습니다: {str(e)}")
    except Exception as e:
        logger.error(f"흐름 삭제 중 오류 발생: {str(e)}")
        raise

def delete_process_from_flow(project_uuid, flow_uuid, process_idx):
    """흐름에서 특정 프로세스를 삭제합니다."""
    flow = get_flow_by_uuid(project_uuid, flow_uuid)
    if flow:
        flow['processes'].pop(process_idx)
        update_flow(project_uuid, flow)
    return flow
