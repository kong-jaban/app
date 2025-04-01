import bcrypt
from db import get_connection

def register_user(username, password, email):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password, email)
            VALUES (%s, %s, %s) RETURNING id
        """, (username, hashed_password, email))
        user_id = cursor.fetchone()[0]
        conn.commit()
        return {"success": True, "user_id": user_id}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()
        
def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            return {"success": True, "user_id": user["id"]}
        else:
            return {"success": False, "error": "Invalid username or password"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()
