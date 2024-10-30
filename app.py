import os
import base64
import logging
from flask import (
    Flask,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    session,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timezone, timedelta
import redis
import uuid
import json

ffrom
flask_mysqldb
import MySQL
from mysql.connector import pooling
from mysql.connector import Error as MySQLError
from cryptography.fernet import Fernet
from flask_wtf import CSRFProtect

# 导入配置类
from config import Config

# 配置日志记录
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.DEBUG)
session["verification_time"] = datetime.now(timezone.utc)
app = Flask(__name__)

# 应用配置
app.config.from_object(Config)

app.config["SESSION_COOKIE_SECURE"] = True
app.config["SECURE_PROXY_SSL_HEADER"] = ("HTTP_X_FORWARDED_PROTO", "https")
csrf = CSRFProtect(app)

mysql_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    host=app.config["MYSQL_HOST"],
    user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_PASSWORD"],
    database=app.config["MYSQL_DB"]
)


def get_db_connection():
    try:
        conn = mysql_pool.get_connection()
        return conn
    except MySQLError as e:
        logging.error(f"数据库连接失败: {e}")
        return None


mysql = MySQL(app)
redis_client = redis.StrictRedis.from_url(app.config["REDIS_URL"])

encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(encryption_key)


def encrypt_data(data):
    return cipher_suite.encrypt(data.encode())


def decrypt_data(data):
    return cipher_suite.decrypt(data).decode()


@app.after_request
def after_request(response):
    session_id = session.get("session_id")
    if session_id:
        session_data = {
            key: value.isoformat() if isinstance(value, datetime) else value
            for key, value in session.items()
        }
        encrypted_data = encrypt_data(json.dumps(session_data))
        redis_client.set(session_id, encrypted_data)
    return response


@app.before_request
def before_request():
    session_id = session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id
        redis_client.set(session_id, encrypt_data("{}"))
    else:
        encrypted_data = redis_client.get(session_id)
        if encrypted_data:
            session_data = decrypt_data(encrypted_data)
            session.update(json.loads(session_data))


@app.route("/set_session_value")
def set_session_value():
    session["key"] = "value"
    return "Session value set"


@app.route("/get_session_value")
def get_session_value():
    return session.get("key", "No value in session")


def generate_verification_code():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])


nickname = "智慧教育平台"
email_address = "206284929@qq.com"

# 对昵称进行Base64编码
encoded_nickname = base64.b64encode(nickname.encode("utf-8")).decode("utf-8")

# 构建完整的'From'头信息
from_header = f"=?utf-8?B?{encoded_nickname}=?= <{email_address}>"


# 发送邮件的函数
def send_verification_email(email, verification_code):
    smtp_server = app.config["SMTP_SERVER"]
    smtp_user = app.config["SMTP_USER"]
    smtp_password = app.config["SMTP_PASSWORD"]
    email_template = """
    您的验证码是：{verification_code}。
    有效期为十分钟，请勿向他人泄露。
    """
    msg = MIMEText(
        email_template.format(verification_code=verification_code), "plain", "utf-8"
    )
    msg["From"] = from_header
    msg["To"] = Header(email, "utf-8")
    msg["Subject"] = Header("您的验证码", "utf-8")
    try:
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email, msg.as_string())
        server.quit()
        session["verification_code"] = verification_code
        session["verification_time"] = datetime.now(timezone.utc)
        return True
    except Exception as e:
        logging.error(f"邮件发送失败: {e}")
        return False


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        passwd = request.form["passwd"]
        email = request.form["email"]
        session["username"] = username

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                flash("该用户名已被注册，请重新输入用户名", "danger")
            else:
                hashed_passwd = generate_password_hash(passwd)
                cursor.execute(
                    """
                  INSERT INTO users (username, passwd, email) VALUES (%s,%s,%s)
              """,
                    (username, hashed_passwd, email),
                )
                conn.commit()
                return redirect(url_for("register_success"))
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        passwd = request.form["passwd"]
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                user = cursor.fetchone()
                if user and check_password_hash(user["passwd"], passwd):
                    session["username"] = username
                    # 登录成功，可以进行进一步的操作
                    return render_template("index.html", username=username)
                else:
                    flash("用户名或密码错误，请检查后重新输入!", "danger")
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
    return render_template("login.html")


@app.route("/")
def index():
    username = None
    if "username" in session:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE username=%s",
                    (session["username"],),
                )
                user = cursor.fetchone()
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("login"))

    return render_template("index.html", username=username)


@app.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        session["username"] = username
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username=%s AND email=%s",
                (username, email),
            )
            user = cursor.fetchone()
            if user:
                verification_code = generate_verification_code()
                if send_verification_email(user["email"], verification_code):
                    session["verification_code"] = verification_code
                    return render_template("verify_code_input.html")
                else:
                    flash("验证码发送失败，请稍后再试。", "danger")
            else:
                flash("该用户名或邮箱错误！请检查后重新填写。", "danger")
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
    return render_template("forget_password.html")


@app.route("/verify_code_input", methods=["GET", "POST"])
def verify_code():
    if request.method == "POST":
        entered_code = request.form["verification_code"]
        # 获取当前UTC时间
        current_time_utc = datetime.now(timezone.utc)

        # 检查会话中是否有验证码和时间
        if "verification_code" in session and "verification_time" in session:
            verification_code_session = session["verification_code"]
            # 将时间字符串转换回datetime对象，并确保它是时区相关的
            verification_time_session = datetime.fromisoformat(
                session["verification_time"]
            ).replace(tzinfo=timezone.utc)

            # 计算时间差
            time_diff = current_time_utc - verification_time_session

            # 检查是否超过10分钟
            if time_diff.total_seconds() > 600:
                flash("验证码已过期，请重新获取。", "danger")
            elif entered_code == verification_code_session:
                # 验证码正确，继续后续操作
                return render_template("reset_password.html")
            else:
                flash("验证码错误，请重新输入。", "danger")
        else:
            flash("验证码无效，请重新获取。", "danger")
    return render_template("verify_code_input.html")


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        new_password = request.form["password1"]
        confirm_password = request.form["password2"]
        username = session.get("username")
        # 确保新密码和确认密码相同
        if new_password != confirm_password:
            flash("两次输入的密码不一致，请检查后重新输入", "danger")
            return redirect(url_for("reset_password"))
        else:
            # 更新数据库中的密码
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                hashed_password = generate_password_hash(new_password)

                cursor.execute(
                    """
                          UPDATE users SET passwd=%s WHERE username=%s
                      """,
                    (hashed_password, username),
                )
                conn.commit()
            except MySQLError as e:
                flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("index"))
    return render_template("reset_password.html")


@app.route("/recommendations")
def recommendations():
    user_id = session.get("user_id")
    if user_id:
        recommended_items = recommend(user_id, item_similarity, user_ratings)
        return render_template(
            "recommendations.html", recommended_items=recommended_items
        )
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    # 启动应用
    app.run(debug=True)
