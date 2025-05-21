import os

def get_file_extension(path):
    base_name = os.path.basename(path.rstrip('/')) # 마지막 '/' 제거 후 이름 추출
    parts = base_name.split('.')
    if len(parts) > 1:
        return parts[-1]
    else:
        return ""
    



