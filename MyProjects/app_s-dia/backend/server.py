from flask import Flask, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from user_manager import login_user as db_login_user
from db import get_connection

app = Flask(__name__)
app.secret_key = "your_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    result = db_login_user(data["username"], data["password"])

    if result["success"]:
        user = User(result["user_id"])
        login_user(user)
        return {"success": True, "message": "Logged in"}
    else:
        return {"success": False, "error": "Invalid username or password"}
    
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return {"success": True, "message": "Logged out"}

@app.route("/check_login", methods=["GET"])
def check_login():
    if current_user.is_authenticated:
        return {"logged_in": True, "user_id": current_user.id}
    else:
        return {"logged_in": False}
