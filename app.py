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
import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector import pooling
from cryptography.fernet import Fernet

# 导入配置类
from config import Config

# 配置日志记录
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)


def generate_secret_key(length=32):
    return os.urandom(length).hex()


app.secret_key = generate_secret_key()
# 应用配置
app.config.from_object(Config)

app.config["SESSION_COOKIE_SECURE"] = True
app.config["SECURE_PROXY_SSL_HEADER"] = ("HTTP_X_FORWARDED_PROTO", "https")

app.config.from_object("config.Config")
redis_client = redis.StrictRedis.from_url(app.config["REDIS_URL"])

encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(encryption_key)

# 数据库连接池配置
dbconfig = {
    "host": app.config["MYSQL_HOST"],
    "user": app.config["MYSQL_USER"],
    "password": app.config["MYSQL_PASSWORD"],
    "database": app.config["MYSQL_DB"],
    "auth_plugin": "mysql_native_password"
}

# 创建连接池
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **dbconfig
)


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
<<<<<<< HEAD
=======
    session.pop("_flashes", None)
>>>>>>> origin/main
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


<<<<<<< HEAD
nickname = "智慧教育平台"
=======
nickname = "cookedman"
>>>>>>> origin/main
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


def init_db():
    create_users_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY, -- 自增主键
        username VARCHAR(255) NOT NULL UNIQUE, -- 用户名，唯一
        passwd VARCHAR(255) NOT NULL, -- 加密后的密码
        email VARCHAR(255) NOT NULL, -- 邮箱地址
<<<<<<< HEAD
        role VARCHAR(50) NOT NULL DEFAULT 'user', -- 用户角色，默认为普通用户
        status VARCHAR(50) NOT NULL DEFAULT 'active', -- 用户状态，默认为激活
=======
>>>>>>> origin/main
        avatar TEXT, -- 用户头像图片链接
        bio TEXT, -- 个人简介
        location VARCHAR(255), -- 用户位置
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 注册时间
        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 最后登录时间，更新时自动更新
    );
    """
    create_login_history_sql = """
    CREATE TABLE IF NOT EXISTS login_history (
<<<<<<< HEAD
        id INT AUTO_INCREMENT PRIMARY KEY, -- 自增主键
        user_id INT NOT NULL, -- 用户ID
        login_time TIMESTAMP NOT NULL, -- 登录时间
        ip_address VARCHAR(255) NOT NULL, -- 登录IP地址
        device_type VARCHAR(50), -- 登录设备类型
        login_result VARCHAR(50) NOT NULL DEFAULT 'success', -- 登录结果，默认为成功
        location VARCHAR(255), -- 登录地理位置
        FOREIGN KEY (user_id) REFERENCES users(id) -- 外键关联用户表
=======
        id INT AUTO_INCREMENT PRIMARY KEY,           -- 自增主键
        username VARCHAR(255) NOT NULL,              -- 用户名
        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- 登录时间
        ip_address VARCHAR(255) NOT NULL,            -- 登录IP地址
        FOREIGN KEY (username) REFERENCES users(username) -- 外键关联用户名
>>>>>>> origin/main
    );
    """
    create_categories_sql = """
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY, -- 菜系ID
        name VARCHAR(255) NOT NULL UNIQUE -- 菜系名称
    );
    """
    create_region_sql = """
    CREATE TABLE IF NOT EXISTS regions (
        id INT AUTO_INCREMENT PRIMARY KEY, -- 地区ID
        name VARCHAR(255) NOT NULL UNIQUE -- 地区名称
    );
    """
    create_stores_sql = """
    CREATE TABLE IF NOT EXISTS stores (
        id INT AUTO_INCREMENT PRIMARY KEY, -- 商店ID
        store_name VARCHAR(255) NOT NULL UNIQUE, -- 商店名称，唯一
        store_image TEXT, -- 图片链接
        permoney INT NOT NULL, -- 人均消费
        commentsnum INT NOT NULL, -- 评论数量
        address TEXT, -- 商店地址
        business_hours TEXT, -- 营业时间
        rating DECIMAL(3, 2), -- 商店评分
        region_id INT, -- 关联地区ID
        FOREIGN KEY (region_id) REFERENCES regions(id)
    );
    """
    create_dishes_sql = """
    CREATE TABLE IF NOT EXISTS dishes(
        id INT AUTO_INCREMENT PRIMARY KEY, -- 菜品ID
        dishes_name VARCHAR(255) NOT NULL UNIQUE, -- 菜品名称，唯一
        score INT NOT NULL, -- 菜品评分
        category_id INT, -- 关联菜系ID
        description TEXT NOT NULL, -- 菜品描述
        price DECIMAL(10, 2) NOT NULL, -- 菜品价格
        image_url TEXT, -- 菜品图片链接
        tags TEXT, -- 菜品标签
<<<<<<< HEAD
        nutrition_facts TEXT, -- 菜品营养成分
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
=======
>>>>>>> origin/main
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 更新时间，更新时自动更新
        deleted_at TIMESTAMP NULL DEFAULT NULL, -- 删除时间，软删除
        store_id INT, -- 关联商店ID
        FOREIGN KEY (category_id) REFERENCES categories(id),
        FOREIGN KEY (store_id) REFERENCES stores(id)
    );
    """
    create_reviews_sql = """
    CREATE TABLE IF NOT EXISTS reviews (
        id INT AUTO_INCREMENT PRIMARY KEY, -- 自增主键
        user_id INT NOT NULL, -- 用户ID
        dish_id INT NOT NULL, -- 菜品ID
        rating INT NOT NULL, -- 评论评分
        comment TEXT NOT NULL, -- 评论内容
        review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 评论时间
        FOREIGN KEY (user_id) REFERENCES users(id), -- 外键关联用户表
        FOREIGN KEY (dish_id) REFERENCES dishes(id) -- 外键关联菜品表
    );
    """
    create_favorites_sql = """
    CREATE TABLE IF NOT EXISTS favorites (
        id INT AUTO_INCREMENT PRIMARY KEY, -- 收藏记录唯一标识符
        user_id INT NOT NULL, -- 关联用户表的ID
        dish_id INT, -- 关联菜品表的ID
        store_id INT, -- 关联商店表的ID
        favorite_time DATETIME DEFAULT CURRENT_TIMESTAMP, -- 收藏时间
        FOREIGN KEY (user_id) REFERENCES users(id), -- 外键，关联到用户表
        FOREIGN KEY (dish_id) REFERENCES dishes(id), -- 外键，关联到菜品表
        FOREIGN KEY (store_id) REFERENCES stores(id) -- 外键，关联到商店表
    );
    """
<<<<<<< HEAD
    create_recommendations_sql="""
=======
    create_likes_sql = """
    CREATE TABLE IF NOT EXISTS likes (
        id INT AUTO_INCREMENT PRIMARY KEY, -- 喜欢记录唯一标识符
        user_id INT NOT NULL, -- 关联用户表的ID
        dish_id INT, -- 关联菜品表的ID
        store_id INT, -- 关联商店表的ID
        like_time DATETIME DEFAULT CURRENT_TIMESTAMP, -- 喜欢时间
        FOREIGN KEY (user_id) REFERENCES users(id), -- 外键，关联到用户表
        FOREIGN KEY (dish_id) REFERENCES dishes(id), -- 外键，关联到菜品表
        FOREIGN KEY (store_id) REFERENCES stores(id) -- 外键，关联到商店表
);
    """
    create_recommendations_sql = """
>>>>>>> origin/main
    CREATE TABLE IF NOT EXISTS recommendations (
        id INT AUTO_INCREMENT PRIMARY KEY, -- 推荐记录唯一标识符
        user_id INT NOT NULL, -- 关联用户表的ID
        dish_id INT, -- 关联菜品表的ID
        store_id INT, -- 关联商店表的ID
        recommendation_time DATETIME DEFAULT CURRENT_TIMESTAMP, -- 推荐时间
        FOREIGN KEY (user_id) REFERENCES users(id), -- 外键，关联到用户表
        FOREIGN KEY (dish_id) REFERENCES dishes(id), -- 外键，关联到菜品表
        FOREIGN KEY (store_id) REFERENCES stores(id) -- 外键，关联到商店表
    );
    """
    try:
<<<<<<< HEAD
        conn = connection_pool.get_connection()
=======
        conn = mysql.connector.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DB"],
            auth_plugin="mysql_native_password",
        )
>>>>>>> origin/main
        cursor = conn.cursor()
        cursor.execute(create_users_sql)
        cursor.execute(create_login_history_sql)
        cursor.execute(create_categories_sql)
        cursor.execute(create_region_sql)
        cursor.execute(create_stores_sql)
        cursor.execute(create_dishes_sql)
        cursor.execute(create_reviews_sql)
        cursor.execute(create_favorites_sql)
<<<<<<< HEAD
=======
        cursor.execute(create_likes_sql)
>>>>>>> origin/main
        cursor.execute(create_recommendations_sql)
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("数据库表创建成功")
    except MySQLError as e:
        logging.error(f"创建表失败: {e}")
<<<<<<< HEAD
=======


def get_db_connection():
    try:
        conn = connection_pool.get_connection()
        print("数据库连接成功")
        return conn
    except MySQLError as e:
        logging.error(f"数据库连接失败: {e}")
        return None
>>>>>>> origin/main


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        passwd = request.form["passwd"]
        email = request.form["email"]
        session["username"] = username
        try:
            conn = mysql.connector.connect(
                host=app.config["MYSQL_HOST"],
                user=app.config["MYSQL_USER"],
                password=app.config["MYSQL_PASSWORD"],
                database=app.config["MYSQL_DB"],
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                flash("该用户名已被注册，请重新输入用户名", "danger")
                return render_template("register.html")
            else:
                hashed_passwd = generate_password_hash(passwd)
                cursor.execute(
                    """
                    INSERT INTO users (username, passwd, email) VALUES (%s, %s, %s)
                    """,                                                                                                                                                                                                                                                                                                                           
                    (username, hashed_passwd, email),
                )
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for("index"))
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("register"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        passwd = request.form["passwd"]
        try:
<<<<<<< HEAD
            conn = mysql.connector.connect(
                host=app.config["MYSQL_HOST"],
                user=app.config["MYSQL_USER"],
                password=app.config["MYSQL_PASSWORD"],
                database=app.config["MYSQL_DB"],
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
=======
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, passwd FROM users WHERE username=%s", (username,)
            )
>>>>>>> origin/main
            user = cursor.fetchone()
            if user and check_password_hash(user["passwd"], passwd):
                session["username"] = username
                ip_address = request.remote_addr
<<<<<<< HEAD
                cursor.execute(
                    "INSERT INTO login_history (user_id, login_time, ip_address) VALUES (%s, %s, %s)",
                    (user["id"], datetime.now(timezone.utc), ip_address),
                )
                conn.commit()
                # 更新用户的最后登录时间
                cursor.execute(
                    "UPDATE users SET last_login=%s WHERE id=%s",
                    (datetime.now(timezone.utc), user["id"]),
=======
                current_time_utc = datetime.now(timezone.utc)
                cursor.execute(
                    "INSERT INTO login_history (username, login_time, ip_address) VALUES (%s, %s, %s)",
                    (username, current_time_utc, ip_address),
                )
                cursor.execute(
                    "UPDATE users SET last_login = %s WHERE username = %s",
                    (current_time_utc, username),
>>>>>>> origin/main
                )
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for("index"))
            else:
                flash("用户名或密码错误，请检查后重新输入!", "danger")
                return redirect(url_for("login"))
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/")
def index():
    username = None
    if "username" in session:
        try:
<<<<<<< HEAD
            conn = mysql.connector.connect(
                host=app.config["MYSQL_HOST"],
                user=app.config["MYSQL_USER"],
                password=app.config["MYSQL_PASSWORD"],
                database=app.config["MYSQL_DB"],
            )
=======
            conn = get_db_connection()
>>>>>>> origin/main
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username=%s",
                (session["username"],),
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            if user:
<<<<<<< HEAD
                return render_template("users.html", user=user)
=======
                return render_template("index.html", user=user)
>>>>>>> origin/main
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("login"))
    return render_template("index.html", user=username)


@app.route("/get_user_location", methods=["GET", "POST"])
def get_user_location():
    if request.method == "GET":
        return render_template("get_user_location.html")
    data = request.json
    lat = data.get("latitude")
    lng = data.get("longitude")
    # 这里可以进一步处理用户的位置信息，例如保存到数据库或进行其他操作
    return jsonify({"status": "success", "message": "Location received"})


@app.route("/forget_passwd", methods=["GET", "POST"])
def forget_passwd():
    if request.method == "POST":
        email = request.form["email"]
        try:
<<<<<<< HEAD
            conn = mysql.connector.connect(
                host=app.config["MYSQL_HOST"],
                user=app.config["MYSQL_USER"],
                password=app.config["MYSQL_PASSWORD"],
                database=app.config["MYSQL_DB"],
            )
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE email=%s",
                (email),
=======
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE email=%s",
                (email,),
>>>>>>> origin/main
            )
            user = cursor.fetchone()
            if user:
                verification_code = generate_verification_code()
                if send_verification_email(user["email"], verification_code):
                    session["verification_code"] = verification_code
                    cursor.close()
                    conn.close()
                    return render_template("verify_code_input.html")
                else:
                    flash("验证码发送失败，请稍后再试。", "danger")
                    return render_template("forget_passwd.html")
            else:
                flash("该用户名或邮箱错误！请检查后重新填写。", "danger")
                return render_template("forget_passwd.html")
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("forget_passwd"))
<<<<<<< HEAD
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
=======
>>>>>>> origin/main
    return render_template("forget_passwd.html")


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
                return render_template("forget_passwd.html")
<<<<<<< HEAD
            elif entered_code == verification_code_session:
=======
            if entered_code == verification_code_session:
>>>>>>> origin/main
                # 验证码正确，继续后续操作
                return render_template("reset_password.html")
            else:
                flash("验证码错误，请重新输入。", "danger")
                return render_template("verify_code_input.html")
        else:
            flash("验证码无效，请重新获取。", "danger")
            return render_template("forget_passwd.html")
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
<<<<<<< HEAD
                conn = mysql.connector.connect(
                    host=app.config["MYSQL_HOST"],
                    user=app.config["MYSQL_USER"],
                    password=app.config["MYSQL_PASSWORD"],
                    database=app.config["MYSQL_DB"],
                )
                cursor = conn.cursor()
=======
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
>>>>>>> origin/main
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
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
            return redirect(url_for("index"))
    return render_template("reset_password.html")


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
<<<<<<< HEAD

    try:
        conn = mysql.connector.connect(
            host=app.config["MYSQL_HOST"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DB"],
        )
=======
    try:
        conn = get_db_connection()
>>>>>>> origin/main
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return render_template("profile.html", user=user)
        else:
            flash("用户信息获取失败", "danger")
            return redirect(url_for("login"))
    except MySQLError as e:
        flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
        return redirect(url_for("login"))


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
<<<<<<< HEAD
        return render_template("reset_passwd.html")
=======
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        # 验证当前密码
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username=%s", (session["username"],)
            )
            user = cursor.fetchone()
            if user and check_password_hash(user["passwd"], current_password):
                # 确保新密码与当前密码不同
                if new_password != current_password:
                    # 确保新密码与确认密码相同
                    if new_password == confirm_password:
                        hashed_password = generate_password_hash(new_password)
                        cursor.execute(
                            "UPDATE users SET passwd=%s WHERE username=%s",
                            (hashed_password, session["username"]),
                        )
                        conn.commit()
                        flash("密码修改成功", "success")
                        return redirect(url_for("profile"))
                    else:
                        flash("新密码与确认密码不一致，请重新输入", "danger")
                        return redirect(url_for("change_password"))
                else:
                    flash("新密码不能与当前密码相同", "danger")
                    return redirect(url_for("change_password"))
            else:
                flash("当前密码输入错误，请重新输入", "danger")
                return redirect(url_for("change_password"))
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("change_password"))
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
>>>>>>> origin/main
    return render_template("change_password.html")


@app.route("/change_email", methods=["GET", "POST"])
def change_email():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        new_email = request.form["new_email"]
        password = request.form["password"]
        try:
<<<<<<< HEAD
            conn = mysql.connector.connect(
                host=app.config["MYSQL_HOST"],
                user=app.config["MYSQL_USER"],
                password=app.config["MYSQL_PASSWORD"],
                database=app.config["MYSQL_DB"],
            )
=======
            conn = get_db_connection()
>>>>>>> origin/main
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE username=%s", (session["username"],)
            )
            user = cursor.fetchone()
            if user and check_password_hash(user["passwd"], password):
                cursor.execute(
                    "UPDATE users SET email=%s WHERE username=%s",
                    (new_email, session["username"]),
                )
                conn.commit()
                flash("邮箱修改成功", "success")
                return redirect(url_for("profile"))
            else:
                flash("密码错误", "danger")
                return redirect(url_for("change_email"))
        except MySQLError as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("change_email"))
    return render_template("change_email.html")


<<<<<<< HEAD
@app.route("/notications", methods=["GET", "POST"])
def notications():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        return render_template("notifications.html")
    return render_template("notications.html")


@app.route("/help", methods=["GET", "POST"])
def help():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        return render_template("help.html")
    return render_template("help.html")


@app.route("/user_agreement", methods=["GET", "POST"])
=======
@app.route("/login_history")
def login_history():
    if "username" not in session:
        return redirect(url_for("login"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM login_history WHERE user_id=(SELECT id FROM users WHERE username=%s)",
            (session["username"],),
        )
        login_history = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("login_history.html", login_history=login_history)
    except mysql.connector.Error as e:
        flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
        return redirect(url_for("login"))


@app.route("/favorites")
def favorites():
    if "username" not in session:
        return redirect(url_for("login"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM favorites WHERE user_id=(SELECT id FROM users WHERE username=%s)",
            (session["username"],),
        )
        favorites = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("favorites.html", favorites=favorites)
    except mysql.connector.Error as e:
        flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
        return redirect(url_for("login"))


@app.route("/reviews")
def reviews():
    if "username" not in session:
        return redirect(url_for("login"))
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM reviews WHERE user_id=(SELECT id FROM users WHERE username=%s)",
            (session["username"],),
        )
        reviews = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("reviews.html", reviews=reviews)
    except mysql.connector.Error as e:
        flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
        return redirect(url_for("login"))


@app.route("/get_dishes_by_category")
def get_dishes_by_category():
    category = request.args.get("category")  # 获取前端传递的分类数据
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # 查询菜品表中 category 字段匹配的菜品
        cursor.execute("SELECT * FROM dishes WHERE category=%s", (category,))
        dishes = cursor.fetchall()
        # 获取对应品的 store_id 并查询对应的店家信息
        stores = []
        for dish in dishes:
            cursor.execute("SELECT * FROM stores WHERE id=%s", (dish["store_id"],))
            store = cursor.fetchone()
            stores.append(store)
        cursor.close()
        conn.close()
        return jsonify({"stores": stores})
    except MySQLError as e:
        logging.error(f"数据库错误: {e.args[0] if e.args else e}")
        return jsonify({"error": "Database error"}), 500


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/everydaylove")
def everydaylove():
    # 这里是路由对应的视图函数
    return render_template("everydaylove.html")


@app.route("/user_agreement")
>>>>>>> origin/main
def user_agreement():
    return render_template("user_agreement.html")


<<<<<<< HEAD
@app.route("/privacy_policy", methods=["GET", "POST"])
=======
@app.route("/notications")
def notications():
    return render_template("notications.html")


@app.route("/privacy_policy")
>>>>>>> origin/main
def privacy_policy():
    return render_template("privacy_policy.html")


<<<<<<< HEAD
@app.route("/about", methods=["GET", "POST"])
=======
@app.route("/about")
>>>>>>> origin/main
def about():
    return render_template("about.html")


<<<<<<< HEAD

=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======

>>>>>>> origin/main
>>>>>>> origin/main
>>>>>>> origin/main
if __name__ == "__main__":
    init_db()
    # 启动应用
    app.run(debug=True)
