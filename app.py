import os
import logging
from flask import Flask, render_template, request, flash, url_for, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime, timezone, timedelta
import redis
import uuid
import json
from flask_mysqldb import MySQL
from mysql.connector import Error as MySQLError

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config.from_object("config.Config")

def get_db_connection():
   try:
       conn = mysql.connection
       return conn
   except MySQLError as e:
       logging.error(f"数据库连接失败: {e}")
       return None
   
app.config.from_object("config.Config")
mysql = MySQL(app)
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)


@app.before_request
def before_request():
    session_id = session.get("session_id")
    if not session_id:
        # 生成一个新的session_id，并设置到cookie中
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id
        # 在Redis中存储一个空会话
        redis_client.set(session_id, "{}")
    else:
        # 从Redis加载会话数据
        session_data = redis_client.get(session_id)
        if session_data:
            session.update(json.loads(session_data))


@app.after_request
def after_request(response):
    session_id = session.get("session_id")
    if session_id:
        # 序列化session字典，并存储到Redis中
        # 检查session中的每个值，如果是datetime对象，则转换为ISO 8601格式的字符串
        session_data = {
            key: value.isoformat() if isinstance(value, datetime) else value
            for key, value in session.items()
        }
        redis_client.set(session_id, json.dumps(session_data))
    return response


@app.route("/set_session_value")
def set_session_value():
    session["key"] = "value"
    return "Session value set"


@app.route("/get_session_value")
def get_session_value():
    return session.get("key", "No value in session")


def generate_verification_code():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

app.config['VERIFICATION_CODE_EXPIRATION'] = int(os.getenv('VERIFICATION_CODE_EXPIRATION', 600))
nickname = "智慧教育平台"
email_address = "206284929@qq.com"

# 对昵称进行Base64编码
encoded_nickname = base64.b64encode(nickname.encode("utf-8")).decode("utf-8")

# 构建完整的'From'头信息
from_header = f"=?utf-8?B?{encoded_nickname}=?= <{email_address}>"

app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
    minutes=30
)  # 设置会话有效期为30分钟


# 发送邮件的函数
def send_verification_email(email, verification_code):
    smtp_server = "smtp.qq.com"
    smtp_user = "206284929@qq.com"
    smtp_password = "ztznowgbfxxnbiei"  # 这是授权码
    msg = MIMEText(
        f"您的验证码是：{verification_code}。有效期为十分钟，请勿向他人泄露。",
        "plain",
        "utf-8",
    )
    msg["From"] = from_header
    msg["To"] = Header(email, "utf-8")
    msg["Subject"] = Header("您的验证码", "utf-8")
    try:
        server = smtplib.SMTP_SSL(smtp_server, 465)
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, email, msg.as_string())
        server.quit()
        # 记录验证码和时间到会话中
        session["verification_code"] = verification_code
        session["verification_time"] = datetime.now()  # 记录当前时间
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False



def init_db():
   create_users_sql = """
     CREATE TABLE IF NOT EXISTS students (
         username VARCHAR(255) NOT NULL,
        passwd VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        PRIMARY KEY (username)
     );
 """
   with get_db_connection() as conn:
       if conn is not None:
           try:
               cursor = conn.cursor()
               cursor.execute(create_users_sql)
               conn.commit()
           except MySQLError as e:
               logging.error(f"创建表失败: {e}")


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
                  INSERT INTO students (username, passwd, email) VALUES (%s,%s,%s)
              """,
                    (username, hashed_passwd, email),
                )
                conn.commit()
                return redirect(url_for("register_success"))
        except Exception as e:
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
        except Exception as e:
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
        except Exception as e:
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
                "SELECT * FROM students WHERE username=%s AND email=%s",
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
        except Exception as e:
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
            except Exception as e:
                flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("reset_password_success"))
    return render_template("reset_password.html")