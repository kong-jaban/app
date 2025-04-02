import os
import json

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), "..", "projects")

if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

def get_project_path(project_name):
    """프로젝트 폴더 경로 반환"""
    return os.path.join(PROJECTS_DIR, project_name)

def list_projects():
    """프로젝트 목록 가져오기"""
    return [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(get_project_path(d))]

def create_project(name):
    """새 프로젝트 생성"""
    project_path = get_project_path(name)
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        with open(os.path.join(project_path, "config.json"), "w") as f:
            json.dump({"name": name}, f)
        return True
    return False

def get_project_csv_path(project_name):
    """프로젝트의 CSV 데이터 경로 반환"""
    return os.path.join(get_project_path(project_name), "data.csv")

def save_processed_data(project_name, df):
    """비식별화된 데이터를 프로젝트 폴더에 저장"""
    processed_path = os.path.join(get_project_path(project_name), "processed.csv")
    df.to_csv(processed_path, index=False)
