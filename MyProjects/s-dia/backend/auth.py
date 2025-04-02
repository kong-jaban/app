from backend.db import insert_user, authenticate_user

def register_user(username, email, password):
    # 사용자가 이미 존재하는지 확인
    existing_user = authenticate_user(email, password)
    if existing_user:
        raise ValueError("사용자가 이미 존재합니다.")
    insert_user(username, email, password)

def login_user(email, password):
    user = authenticate_user(email, password)
    if user:
        return user
    else:
        raise ValueError("잘못된 이메일 또는 비밀번호입니다.")
