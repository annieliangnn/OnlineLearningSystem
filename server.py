import flask
import re
import pymysql
from flask import Flask, request, redirect, url_for, render_template, session

# 初始化
app = flask.Flask(__name__)
# 使用pymysql.connect方法连接本地mysql数据库
db = pymysql.connect(host='localhost', port=3306, user='root',
                     password='123456', database='learningmanagementsystem', charset='utf8')
# 操作数据库，获取db下的cursor对象
cursor = db.cursor()
# 存储登陆用户的名字用户其它网页的显示
users = []

app.secret_key = 'carson1'  # 会话密钥，用于保护session


def is_logged_in():
    return 'login' in session and session['login'] == 'OK'


def get_user_role():
    return session.get('role', None)


@app.route('/')
def main():
    student_courses = get_student_courses()
    teacher_upload_list = get_teacher_courses()

    if is_logged_in():
        # 用户已登录，根据角色重定
        return redirect(url_for('login'))
    else:
        # 用户未登录，显示首页面并提供登录选项
        return render_template('firstpage.html', student_courses=student_courses,
                               teacher_upload_list=teacher_upload_list)


@app.route("/login", methods=["GET", "POST"])
def login():
    session['login'] = ''
    msg = ''
    user = ''
    if request.method == 'POST':
        user = request.form.get("user", "")
        pwd = request.form.get("pwd", "")
        role = request.form.get("role", "")

        if re.match(r"^[a-zA-Z]+$", user) and re.match(r"^[a-zA-Z\d]+$", pwd):
            # 定义 SQL 查询模板
            sql = "SELECT * FROM {} WHERE Name=%s AND Password=%s;"
            if role == 'admin':
                table = 'administrator'
            elif role == 'instructor':
                table = 'instructor'
            elif role == 'student':
                table = 'student'
            else:
                # msg = 'Invalid role selected'
                return render_template('login.html', msg=msg, user=user)

            # 执行参数化查询
            cursor.execute(sql.format(table), (user, pwd))
            result = cursor.fetchone()
            if result:
                session['login'] = 'OK'
                session['username'] = user  # 存储登录成功的用户名用于显示
                session['role'] = role  # 存储用户角色
                return redirect(url_for('admin_dashboard'))
            else:
                msg = 'User name or password is wrong'
        else:
            msg = 'Invalid input'

    return render_template('login.html', msg=msg, user=user)


@app.route('/student_courses')
def student_courses():
    # Fetch and display the course list for students
    if is_logged_in() and get_user_role() == 'student':
        # Assume get_student_courses() fetches the course data
        courses = get_student_courses()
        return render_template('student_courses.html', courses=courses)
    else:
        return redirect(url_for('login'))


@app.route('/instructor_uploads')
def instructor_uploads():
    # Fetch and display the upload list for instructors
    if is_logged_in() and get_user_role() == 'instructor':
        # Assume get_teacher_courses() fetches the upload data
        uploads = get_teacher_courses()
        return render_template('instructor_uploads.html', uploads=uploads)
    else:
        return redirect(url_for('login'))


def is_admin():
    return session.get('login') == 'OK' and session.get('role') == 'admin'


def is_instructor():
    return session.get('login') == 'OK' and session.get('role') == 'instructor'


def is_student():
    return session.get('login') == 'OK' and session.get('role') == 'student'


# 假设这是您的数据库查询函数，返回学生和教师的课程列表和上传列表
def get_student_courses():
    # 查询并返回学生的课程列表
    # 查询学生的课程列表
    student_course_list = []
    try:
        sql = "SELECT courseID FROM student;"
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            course_id = row[0]
            student_course_list.append(course_id)
    except Exception as e:
        print("Error fetching student courses:", e)
    finally:
        db.close()
    return student_course_list


def get_teacher_courses():
    # 查询并返回教师的课程上传列表
    teacher_upload_list = []
    try:
        sql = "SELECT courseID FROM instructor;"
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            course_id = row[0]
            teacher_upload_list.append(course_id)
    except Exception as e:
        print("Error fetching teacher upload courses:", e)

    return teacher_upload_list


# 管理员页面路由
@app.route("/admin_dashboard", methods=['GET', 'POST'])
def admin_dashboard():
    # login session值
    if flask.session.get("login", "") == '':
        # 用户没有登陆
        print('用户还没有登陆!即将重定向!')
        return flask.redirect('/')
    insert_result = ''
    # 获取学生和教师的课程列表和上传列表
    student_courses = get_student_courses()
    teacher_upload_list = get_teacher_courses()
    if is_logged_in() and get_user_role() == 'admin':
        return render_template('admin_homepage.html', student_courses=student_courses,
                               teacher_upload_list=teacher_upload_list)
    else:
        return redirect(url_for('login'))


# # 添加学生功能
# @app.route("/admin/add_student", methods=["POST"])
# def add_student():
#     if is_admin():
#         if request.method == "POST":
#             student_id = request.form.get("student_id")
#             name = request.form.get("name")
#             courseid = request.form.get("courseid")
#             lecture = request.form.get("lecture")
#             password = request.form.get("password")
#             # 将学生信息插入数据库
#             cursor.execute(
#                 "INSERT INTO student (StudentID, Name, CourseID, Lecture, Password) VALUES (%s, %s, %s, %s, %s);",
#                 (student_id, name, courseid, lecture, password))
#             db.commit()
#             return redirect(url_for('admin_dashboard'))
#     else:
#         return redirect(url_for('login'))
#
#
# # 编辑学生信息功能
# @app.route("/admin/edit_student/<int:student_id>", methods=["GET", "POST"])
# def edit_student(student_id):
#     if is_admin():
#         if request.method == "POST":
#             name = request.form.get("name")
#             courseid = request.form.get("courseid")
#             lecture = request.form.get("lecture")
#             password = request.form.get("password")
#             # 更新学生信息
#             cursor.execute("UPDATE student SET Name=%s, CourseID=%s, Lecture=%s, Password=%s WHERE StudentID=%s;",
#                            (name, courseid, lecture, password, student_id))
#             db.commit()
#             return redirect(url_for('admin_dashboard'))
#         else:
#             # 查询要编辑的学生信息并在页面显示
#             cursor.execute("SELECT * FROM student WHERE StudentID=%s;", (student_id,))
#             student = cursor.fetchone()
#             cursor.execute("SELECT * FROM student;")
#             students = cursor.fetchall()
#             return render_template('admin_homepage.html', student=student, students=students)
#     else:
#         return redirect(url_for('login'))
#
#
# # 删除学生功能
# @app.route("/admin/delete_student/<int:student_id>")
# def delete_student(student_id):
#     if is_admin():
#         # 删除指定学生
#         cursor.execute("DELETE FROM student WHERE StudentID=%s;", (student_id,))
#         db.commit()
#         return redirect(url_for('admin_dashboard'))
#     else:
#         return redirect(url_for('login'))
#
#
# # 搜索学生功能
# @app.route("/admin/search_student", methods=["POST"])
# def search_student():
#     if is_admin():
#         if request.method == "POST":
#             keyword = request.form.get("keyword")
#             # 在数据库中搜索学生
#             cursor.execute("SELECT * FROM student WHERE Name LIKE %s;", ('%' + keyword + '%',))
#             students = cursor.fetchall()
#             return render_template('admin_homepage.html', students=students)
#     else:
#         return redirect(url_for('login'))


# 启动服务器
app.debug = True
# 增加session会话保护(任意字符串,用来对session进行加密)
app.secret_key = 'carson1'
try:
    app.run()
except Exception as err:
    print(err)
    db.close()  # 关闭数据库连接
