import psycopg2
from psycopg2 import sql

# PostgreSQL 데이터베이스 연결
def connect_db():
    conn = psycopg2.connect(
        dbname="your_db_name", 
        user="your_db_user", 
        password="your_db_password", 
        host="localhost", 
        port="5432"
    )
    return conn

# 사용자 인증 함수 (로그인)
def authenticate_user(username, password):
    conn = connect_db()
    cur = conn.cursor()
    query = sql.SQL("SELECT * FROM users WHERE username = %s AND password = %s")
    cur.execute(query, (username, password))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result  # 결과가 있으면 사용자 존재, 없으면 None 반환
