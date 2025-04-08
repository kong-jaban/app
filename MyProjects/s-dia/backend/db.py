import psycopg2
from psycopg2 import sql
import hashlib

DB_CONFIG = {
    'dbname': 'sdiadb',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}

def get_db_connection():
    import locale
    print("Default encoding:", locale.getpreferredencoding())
    print("DB_CONFIG:", DB_CONFIG)
    return psycopg2.connect(**DB_CONFIG, client_encoding='UTF8')


def create_users_table():
    """Users 테이블 생성"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def hash_password(password):
    """비밀번호를 SHA-256으로 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """새 사용자 등록"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        hashed_pw = hash_password(password)
        cur.execute("""
            INSERT INTO users (username, email, password_hash) 
            VALUES (%s, %s, %s)
        """, (username, email, hashed_pw))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def check_login(username, password):
    """로그인 정보 확인"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    hashed_pw = hash_password(password)
    cur.execute("""
        SELECT * FROM users WHERE username = %s AND password_hash = %s
    """, (username, hashed_pw))
    
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    return user is not None

def verify_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    
    hashed_pw = hash_password(password)
    cur.execute(
        "SELECT * FROM users WHERE username = %s AND password_hash = %s",
        (username, hashed_pw)
    )
    
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None