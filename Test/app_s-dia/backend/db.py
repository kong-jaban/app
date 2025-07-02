import psycopg2
import subprocess
import psycopg2
import time
# PostgreSQL 연결 설정
DB_CONFIG = {
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def connect_db():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print("데이터베이스 연결 실패:", e)
        return None

def verify_login(username, password):
    """사용자 인증"""
    conn = connect_db()
    if conn is None:
        return False

    try:
        cur = conn.cursor()
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cur.execute(query, (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        return user is not None
    except Exception as e:
        print("로그인 확인 중 오류 발생:", e)
        return False
import psycopg2

DB_CONFIG = {
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

def start_postgres():
    """PostgreSQL 서버 실행"""
    try:
        # Windows 기준 PostgreSQL 서비스 시작
        subprocess.run(["pg_ctl", "start", "-D", "C:\\Program Files\\PostgreSQL\\15\\data"], check=True)
        print("PostgreSQL 서버를 시작했습니다.")
        time.sleep(5)  # 서버가 실행될 시간을 줌
    except Exception as e:
        print(f"PostgreSQL 실행 실패: {e}")

def create_users_table():
    """users 테이블 생성"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        conn.commit()
        cur.close()
        print("users 테이블 생성 완료")
    except Exception as e:
        print(f"DB 오류: {e}")
    finally:
        if conn:
            conn.close()
if __name__ == "__main__":
    start_postgres()
    create_users_table()