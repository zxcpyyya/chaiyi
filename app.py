import base64
from flask import Flask, render_template, request, flash, url_for, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from zhipuai import ZhipuAI
from datetime import datetime, timezone, timedelta
import redis
import uuid
import json

app = Flask(__name__)
app.config.from_object("config.Config")

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.before_request
def before_request():
    session_id = session.get('session_id')
    if not session_id:
        # 生成一个新的session_id，并设置到cookie中
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        # 在Redis中存储一个空会话
        redis_client.set(session_id, '{}')
    else:
        # 从Redis加载会话数据
        session_data = redis_client.get(session_id)
        if session_data:
            session.update(json.loads(session_data))


@app.after_request
def after_request(response):
    session_id = session.get('session_id')
    if session_id:
        # 序列化session字典，并存储到Redis中
        # 检查session中的每个值，如果是datetime对象，则转换为ISO 8601格式的字符串
        session_data = {key: value.isoformat() if isinstance(value, datetime) else value for key, value in
                        session.items()}
        redis_client.set(session_id, json.dumps(session_data))
    return response


@app.route('/set_session_value')
def set_session_value():
    session['key'] = 'value'
    return 'Session value set'


@app.route('/get_session_value')
def get_session_value():
    return session.get('key', 'No value in session')


def generate_verification_code():
    return "".join([str(random.randint(0, 9)) for _ in range(6)])


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


def get_db_connection():
    try:
        conn = sqlite3.connect("my_database.db", detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"数据库连接失败: {e}")
        return None


def init_db():
    create_students_sql = """
      CREATE TABLE IF NOT EXISTS students (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          student_id TEXT NOT NULL,
          password TEXT NOT NULL,
          email TEXT NOT NULL
      );
  """
    create_courses_sql = """
      CREATE TABLE IF NOT EXISTS courses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          description TEXT NOT NULL,
          difficulty TEXT NOT NULL,
          video_url TEXT NOT NULL
      );
  """
    create_notifications_sql = """
      CREATE TABLE IF NOT EXISTS notifications (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          timestamp DATETIME NOT NULL
      );
  """
    create_discussions_sql = """
      CREATE TABLE IF NOT EXISTS discussions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          student_id TEXT NOT NULL,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          timestamp DATETIME NOT NULL
      );
  """
    create_replies_sql = """
      CREATE TABLE IF NOT EXISTS replies (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          discussion_id INTEGER NOT NULL,
          student_id TEXT NOT NULL,
          content TEXT NOT NULL,
          timestamp DATETIME NOT NULL,
          FOREIGN KEY (discussion_id) REFERENCES discussions (id)
      );
  """
    create_exams_sql = """
           CREATE TABLE IF NOT EXISTS exams (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               description TEXT NOT NULL,
               difficulty TEXT NOT NULL,
               total_score INTEGER NOT NULL,
               single_choice_count INTEGER NOT NULL,
               fill_in_the_blank_count INTEGER NOT NULL,
               exam_time INTEGER NOT NULL,
               created_by TEXT NOT NULL,
               timestamp DATETIME NOT NULL
);
       """
    create_questions_sql = """
           CREATE TABLE IF NOT EXISTS questions (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               exam_id INTEGER NOT NULL,
               question_text TEXT NOT NULL,
               option_a TEXT,
               option_b TEXT,
               option_c TEXT,
               option_d TEXT,
               correct_answer TEXT,
               question_type TEXT NOT NULL,
               score INTEGER NOT NULL,
               FOREIGN KEY (exam_id) REFERENCES exams (id)
           );
       """
    create_answers_sql = """
           CREATE TABLE IF NOT EXISTS answers (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               student_id TEXT NOT NULL,
               exam_id INTEGER NOT NULL,
               question_id INTEGER NOT NULL,
               selected_answer TEXT NOT NULL,
               correct_answer TEXT,
               score INTEGER NOT NULL,
               FOREIGN KEY (student_id) REFERENCES students (student_id),
               FOREIGN KEY (exam_id) REFERENCES exams (id),
               FOREIGN KEY (correct_answer) REFERENCES questions (correct_answer),
               FOREIGN KEY (question_id) REFERENCES questions (id)
           );
       """

    with get_db_connection() as conn:
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute(create_students_sql)
                cursor.execute(create_courses_sql)
                cursor.execute(create_notifications_sql)
                cursor.execute(create_discussions_sql)
                cursor.execute(create_replies_sql)
                cursor.execute(create_exams_sql)
                cursor.execute(create_questions_sql)
                cursor.execute(create_answers_sql)
                conn.commit()
            except sqlite3.Error as e:
                print(f"创建表失败: {e}")


def get_user_role(student_id):
    if student_id == "2215304122":
        return "admin"
    elif student_id.startswith("11"):
        return "teacher"
    elif student_id.startswith("22"):
        return "student"
    else:
        return "unknown"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        student_id = request.form["student_id"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        email = request.form["email"]
        session["student_id"] = student_id

        if password1 != password2:
            flash("两次密码输入不一致，请重新输入", "danger")
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM students WHERE student_id=?", (student_id,)
                )
                if cursor.fetchone():
                    flash("该学号或工号已经注册过", "danger")
                else:
                    hashed_password = generate_password_hash(password1)
                    cursor.execute(
                        """
                      INSERT INTO students (name, student_id, password, email) VALUES (?, ?, ?, ?)
                  """,
                        (name, student_id, hashed_password, email),
                    )
                    conn.commit()
                    return redirect(url_for("register_success"))
            except sqlite3.Error as e:
                flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        student_id = request.form["student_id"]
        password = request.form["password"]
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM students WHERE student_id=?", (student_id,)
                )
                user = cursor.fetchone()
                if user and check_password_hash(user["password"], password):
                    session["student_id"] = student_id
                    # 登录成功，可以进行进一步的操作
                    return render_template("index.html", user=user)
                else:
                    flash("学号或工号或密码错误，请检查后重新输入", "danger")
        except sqlite3.Error as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
    return render_template("login.html")


@app.route("/")
def index():
    user = None
    if "student_id" in session:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM students WHERE student_id=?",
                    (session["student_id"],),
                )
                user = cursor.fetchone()
        except sqlite3.Error as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("login"))

    return render_template("index.html", user=user)


@app.route("/forget_password", methods=["GET", "POST"])
def forget_password():
    if request.method == "POST":
        student_id = request.form["student_id"]
        email = request.form["email"]
        session["student_id"] = student_id
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM students WHERE student_id=? AND email=?",
                (student_id, email),
            )
            user = cursor.fetchone()
            if user:
                # 直接通过键名访问列的值
                print("ID:", user["id"])
                print("Name:", user["name"])
                print("Student ID:", user["student_id"])
                print("Email:", user["email"])
                # 如果找到用户，生成验证码并发送邮件
                verification_code = generate_verification_code()
                if send_verification_email(user["email"], verification_code):
                    session["verification_code"] = verification_code
                    return render_template("verify_code_input.html")
                    # 将验证码和用户ID存储在会话中
                else:
                    flash("验证码发送失败，请稍后再试。", "danger")
            else:
                flash("该学号或邮箱错误！请检查后重新填写。", "danger")
        except sqlite3.Error as e:
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
            verification_time_session = datetime.fromisoformat(session["verification_time"]).replace(
                tzinfo=timezone.utc)

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
        student_id = session.get("student_id")
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
                          UPDATE students SET password=? WHERE student_id=?
                      """,
                    (hashed_password, student_id),
                )
                conn.commit()
            except sqlite3.Error as e:
                flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
            return redirect(url_for("reset_password_success"))
    return render_template("reset_password.html")


@app.route("/reset_password_success", methods=["GET", "POST"])
def reset_password_success():
    if request.method == "POST":
        return render_template("login.html")
    return render_template("reset_password_success.html")


@app.route("/register_success", methods=["GET", "POST"])
def register_success():
    if request.method == "POST":
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM students WHERE student_id=?",
                    (session["student_id"],),
                )
                user = cursor.fetchone()
        except sqlite3.Error as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
        return render_template("index.html", user=user)
    return render_template("register_success.html")


client = ZhipuAI(api_key="aefb1b0854138803d342f319d9ca9ff8.mDMe8UQ7P9KZbnTQ")


@app.route("/ai_assistant", methods=["GET", "POST"])
def ai_assistant():
    if "student_id" not in session:
        # 如果用户未登录，重定向到登录页面
        return redirect(url_for("login"))

    chat_history = session.get("chat_history", [])
    user_question = ""
    ai_answer = ""

    if request.method == "POST":
        user_question = request.form["question"]
        try:
            response = client.chat.completions.create(
                model="glm-4",
                messages=[{"role": "user", "content": user_question}],
            )
            ai_answer = response.choices[0].message.content
            # 将用户问题和AI的回答添加到对话历史中
            chat_history.append((user_question, ai_answer))
        except Exception as e:
            ai_answer = f"AI助手出现错误：{str(e)}"
            flash("AI助手无法回答问题，请稍后再试。", "danger")

    # 更新会话中的对话历史
    session["chat_history"] = chat_history

    return render_template(
        "ai_assistant.html",
        question=user_question,
        answer=ai_answer,
        chat_history=chat_history,
    )



@app.route("/logout")
def logout():
    session.clear()  # 清除会话中的所有信息
    return redirect(url_for("index"))


@app.route("/add_notifications", methods=["GET", "POST"])
def add_notifications():
    if "student_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notifications (title, content, timestamp) VALUES (?, ?, ?)",
                (title, content, timestamp),
            )
            conn.commit()
            conn.close()
            session["success_message"] = "通知添加成功！"
            return redirect(url_for("success"))
        except sqlite3.Error as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
    return render_template("add_notifications.html")


@app.route("/notifications")
def notifications():
    if "student_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notifications ORDER BY timestamp DESC")
    notifications = cursor.fetchall()

    # 将Row对象转换为字典，并格式化时间戳
    formatted_notifications = []
    for notification in notifications:
        notification_dict = dict(notification)
        notification_dict['formatted_timestamp'] = datetime.strptime(notification_dict['timestamp'],
                                                                     "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        formatted_notifications.append(notification_dict)

    conn.close()

    return render_template("notifications.html", notifications=formatted_notifications)




@app.route("/discussions")
def discussions():
    if "student_id" not in session:
        return redirect(url_for("login"))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM discussions ORDER BY timestamp DESC")
            discussions = cursor.fetchall()
            # 将时间字符串转换为 datetime 对象，并截断到秒
            discussions_list = []
            for discussion in discussions:
                time_str = discussion["timestamp"]
                time_str = time_str[:19]  # 截断到秒
                discussion_dict = dict(discussion)
                discussion_dict["timestamp"] = datetime.strptime(
                    time_str, "%Y-%m-%d %H:%M:%S"
                )
                discussions_list.append(discussion_dict)
            return render_template("discussions.html", discussions=discussions_list)
    except sqlite3.Error as e:
        flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
        return redirect(url_for("index"))


@app.route("/create_discussion", methods=["GET", "POST"])
def create_discussion():
    if "student_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        student_id = session["student_id"]
        timestamp = datetime.now()

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                   INSERT INTO discussions (student_id, title, content, timestamp) VALUES (?, ?, ?, ?)
               """,
                    (student_id, title, content, timestamp),
                )
                conn.commit()
                return redirect(url_for("discussions"))
        except sqlite3.Error as e:
            flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")

    return render_template("create_discussion.html")


@app.route("/delete_discussion/<int:discussion_id>", methods=["DELETE"])
def delete_discussion(discussion_id):
    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 检查讨论帖是否存在
            cursor.execute("SELECT * FROM discussions WHERE id=?", (discussion_id,))
            discussion = cursor.fetchone()
            if not discussion:
                flash("讨论帖不存在", "danger")
                return redirect(url_for("discussions"))

            # 检查权限
            if discussion['student_id'] != student_id and student_id != "2215304122":
                flash("您没有权限删除该讨论帖", "danger")
                return redirect(url_for("discussion_detail", discussion_id=discussion_id))

            # 删除讨论帖及其所有回复
            cursor.execute("DELETE FROM replies WHERE discussion_id=?", (discussion_id,))
            cursor.execute("DELETE FROM discussions WHERE id=?", (discussion_id,))
            conn.commit()
            flash("讨论帖已删除", "success")
    except sqlite3.Error as e:
        flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")

    return redirect(url_for("discussions"))


@app.route("/discussion/<int:discussion_id>")
def discussion_detail(discussion_id):
    if "student_id" not in session:
        return redirect(url_for("login"))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM discussions WHERE id=?", (discussion_id,))
            discussion = cursor.fetchone()
            if discussion:
                discussion = dict(discussion)
                discussion['timestamp'] = discussion['timestamp'][:19]  # 截断到秒

            cursor.execute(
                "SELECT * FROM replies WHERE discussion_id=? ORDER BY timestamp ASC",
                (discussion_id,),
            )
            replies = cursor.fetchall()
            replies_list = []
            for reply in replies:
                reply_dict = dict(reply)
                reply_dict['timestamp'] = reply_dict['timestamp'][:19]  # 截断到秒
                replies_list.append(reply_dict)

            return render_template(
                "discussion_detail.html", discussion=discussion, replies=replies_list
            )
    except sqlite3.Error as e:
        flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")
        return redirect(url_for("discussions"))


@app.route('/reply', methods=['POST'])
def reply():
    content = request.form.get('content')
    discussion_id = request.form.get('discussion_id')
    student_id = session.get('student_id')  # 获取当前登录的学生ID
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not content or not discussion_id or not student_id:
        app.logger.error('Invalid input, content, discussion_id, and student_id are required')
        return jsonify({'error': 'Invalid input, content, discussion_id, and student_id are required'}), 400

    # 保存回复到数据库
    try:
        conn = sqlite3.connect('my_database.db')
        cursor = conn.cursor()
        cursor.execute('''
           INSERT INTO replies (discussion_id, student_id, content, timestamp)
           VALUES (?, ?, ?, ?)
       ''', (discussion_id, student_id, content, timestamp))
        conn.commit()
        reply_id = cursor.lastrowid  # 获取新插入回复的ID
    except sqlite3.Error as e:
        app.logger.error('Database error: ' + str(e))
        return jsonify({'error': 'Database error'}), 500
    finally:
        if conn:
            conn.close()

    # 返回新回复的数据
    return jsonify({
        'discussion_id': discussion_id,
        'student_id': student_id,
        'content': content,
        'timestamp': timestamp,
        'id': reply_id  # 包含新回复的ID
    })


@app.route("/delete_reply/<int:reply_id>", methods=["POST"])
def delete_reply(reply_id):
    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 检查评论是否存在
            cursor.execute("SELECT * FROM replies WHERE id=?", (reply_id,))
            reply = cursor.fetchone()
            if not reply:
                flash("评论不存在", "danger")
                return redirect(url_for("discussion_detail", discussion_id=reply['discussion_id']))

            # 检查权限
            if reply['student_id'] != student_id and student_id != "2215304122":
                flash("您没有权限删除该评论", "danger")
                return redirect(url_for("discussion_detail", discussion_id=reply['discussion_id']))

            # 删除评论
            cursor.execute("DELETE FROM replies WHERE id=?", (reply_id,))
            conn.commit()
            flash("评论已删除", "success")
    except sqlite3.Error as e:
        flash(f"数据库错误: {e.args[0] if e.args else e}", "danger")

    return redirect(url_for("discussion_detail", discussion_id=reply['discussion_id']))



@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
