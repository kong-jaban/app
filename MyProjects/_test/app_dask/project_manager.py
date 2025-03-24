import os
import json

PROJECTS_DIR = "projects"

# 폴더가 없으면 생성
if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

def create_project(name):
    os.makedirs(os.path.join(PROJECTS_DIR, name), exist_ok=True)
    config_path = os.path.join(PROJECTS_DIR, name, "config.json")
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({}, f)

def list_projects():
    return [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]
