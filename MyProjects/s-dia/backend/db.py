import psycopg2
from psycopg2 import sql
import hashlib

DB_CONFIG = {
    "dbname": "my_database",  # 영어만 사용
    "user": "postgres",
    "password": "securepassword123",  # 특수문자 없는 영문+숫자로 변경
    "host": "localhost",
    "port": "5432",
}

def get_db_connection():
    dsn = "dbname=my_database user=postgres password=mypassword123 host=localhost port=5432"
    return psycopg2.connect(dsn, client_encoding='UTF8')

def create_users_table():
    """Users 테이블 생성"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
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
