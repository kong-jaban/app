import os
import json
import shutil

PROJECTS_DIR = "projects"

def create_project(name):
    os.makedirs(os.path.join(PROJECTS_DIR, name), exist_ok=True)
    config_path = os.path.join(PROJECTS_DIR, name, "config.json")
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({}, f)

def list_projects():
    return [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]

def get_project_path(name):
    return os.path.join(PROJECTS_DIR, name)

def save_project_config(name, config):
    config_path = os.path.join(get_project_path(name), "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f)

def load_project_config(name):
    config_path = os.path.join(get_project_path(name), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}