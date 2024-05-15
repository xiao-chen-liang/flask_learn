import json
import random
import sqlite3
import string
import time
from functools import wraps

from flask import Flask, request, Responser

app = Flask(__name__)

# 增删改查简单封装
def RunSqlite(db, table, action, field, value):
    connect = sqlite3.connect(db)
    cursor = connect.cursor()

    # 执行插入动作
    if action == "insert":
        insert = f"insert into {table}({field}) values({value});"
        if insert == None or len(insert) == 0:
            return False
        try:
            cursor.execute(insert)
        except Exception:
            return False

    # 执行更新操作
    elif action == "update":
        update = f"update {table} set {value} where {field};"
        if update == None or len(update) == 0:
            return False
        try:
            cursor.execute(update)
        except Exception:
            return False

    # 执行查询操作
    elif action == "select":

        # 查询条件是否为空
        if value == "none":
            select = f"select {field} from {table};"
        else:
            select = f"select {field} from {table} where {value};"

        try:
            ref = cursor.execute(select)
            ref_data = ref.fetchall()
            connect.commit()
            connect.close()
            return ref_data
        except Exception:
            return False

    # 执行删除操作
    elif action == "delete":
        delete = f"delete from {table} where {field};"
        if delete == None or len(delete) == 0:
            return False
        try:
            cursor.execute(delete)
        except Exception:
            return False
    try:
        connect.commit()
        connect.close()
        return True
    except Exception:
        return False


@app.route("/create", methods=["GET"])
def create():
    conn = sqlite3.connect("./database.db")
    cursor = conn.cursor()
    create_auth = "create table UserAuthDB(" \
                  "id INTEGER primary key AUTOINCREMENT not null unique," \
                  "username varchar(64) not null unique," \
                  "password varchar(64) not null" \
                  ")"
    cursor.execute(create_auth)

    create_session = "create table SessionAuthDB(" \
                     "id INTEGER primary key AUTOINCREMENT not null unique," \
                     "username varchar(64) not null unique," \
                     "token varchar(128) not null unique," \
                     "invalid_date int not null" \
                     ")"

    cursor.execute(create_session)
    conn.commit()
    cursor.close()
    conn.close()
    return "create success"


# 验证用户名密码是否合法
def CheckParameters(*kwargs):
    for item in range(len(kwargs)):
        # 先验证长度
        if len(kwargs[item]) >= 256 or len(kwargs[item]) == 0:
            return False

        # 先小写,然后去掉两侧空格,去掉所有空格
        local_string = kwargs[item].lower().strip().replace(" ", "")

        # 判断是否只包含 大写 小写 数字
        for kw in local_string:
            if kw.isupper() != True and kw.islower() != True and kw.isdigit() != True:
                return False
    return True


# 登录认证模块
@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        # 获取参数信息
        obtain_dict = request.form.to_dict()
        if len(obtain_dict) != 0 and len(obtain_dict) == 2:
            username = obtain_dict["username"]
            password = obtain_dict["password"]

            # 验证是否合法
            is_true = CheckParameters(username, password)
            if is_true == True:

                # 查询是否存在该用户
                select = RunSqlite("./database.db", "UserAuthDB", "select", "username,password",
                                   f"username='{username}'")
                if select[0][0] == username and select[0][1] == password:
                    # 查询Session列表是否存在
                    select_session = RunSqlite("./database.db", "SessionAuthDB", "select", "token",
                                               f"username='{username}'")
                    if select_session != []:
                        ref = {"message": ""}
                        ref["message"] = select_session[0][0]
                        return json.dumps(ref, ensure_ascii=False)

                    # Session不存在则需要重新生成
                    else:
                        # 生成并写入token和过期时间戳
                        token = ''.join(random.sample(string.ascii_letters + string.digits, 32))

                        # 设置360秒周期,过期时间
                        time_stamp = int(time.time()) + 360

                        insert = RunSqlite("./database.db", "SessionAuthDB", "insert", "username,token,invalid_date",
                                           f"'{username}','{token}',{time_stamp}")
                        if insert == True:
                            ref = {"message": ""}
                            ref["message"] = token
                            return json.dumps(ref, ensure_ascii=False)
                else:
                    return json.dumps("{'message': '用户名或密码错误'}", ensure_ascii=False)
            else:
                return json.dumps("{'message': '输入参数不可用'}", ensure_ascii=False)

    return json.dumps("{'message': '未知错误'}", ensure_ascii=False)


# 检查登录状态 token是否过期的装饰器
def login_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("处理登录逻辑部分: {}".format(request.url))

        # 得到token 验证是否登陆了,且token没有过期
        local_timestamp = int(time.time())
        get_token = request.headers.get("token")

        # 验证传入参数是否合法
        if CheckParameters(get_token) == True:
            select = RunSqlite("./database.db", "SessionAuthDB", "select", "token,invalid_date", f"token='{get_token}'")
            print(select)
            # 判断是否存在记录,如果存在,在判断时间戳是否合理
            if select != []:
                # 如果当前时间与数据库比对,大于说明过期了需要删除原来的,让用户重新登录
                if local_timestamp >= int(select[0][1]):
                    print("时间戳过期了")
                    # 删除原来的Token
                    delete = RunSqlite("./database.db", "SessionAuthDB", "delete", f"token='{get_token}'", "none")
                    if delete == True:
                        return json.dumps("{'token': 'Token 已过期,请重新登录获取'}", ensure_ascii=False)
                    else:
                        return json.dumps("{'token': '数据库删除异常,请联系开发者'}", ensure_ascii=False)
                else:
                    # 验证Token是否一致
                    if select[0][0] == get_token:
                        print("Token验证正常,继续执行function_ptr指向代码.")
                        # 返回到原函数
                        return func(*args, **kwargs)
                    else:
                        print("Token验证错误 {}".format(select))
                        return json.dumps("{'token': 'Token 传入错误'}", ensure_ascii=False)

            # 装饰器调用原函数
            # function_ptr = func(*args, **kwargs)

        return json.dumps("{'token': 'Token 验证失败'}", ensure_ascii=False)

    return wrapper


# 获取参数函数
@app.route("/GetPage", methods=["POST"])
@login_check
def GetPage():
    if request.method == "POST":
        # 获取参数信息
        obtain_dict = request.form.to_dict()
        if len(obtain_dict) != 0 and len(obtain_dict) == 1:

            pagename = obtain_dict["pagename"]
            print("查询名称: {}".format(obtain_dict["pagename"]))

            # 相应头的完整写法
            req = Response(response="ok", status=200, mimetype="application/json")
            req.headers["Content-Type"] = "text/json; charset=utf-8"
            req.headers["Server"] = "LyShark Server 1.0"
            req.data = json.dumps("{'message': 'hello world'}")
            return req
        else:
            return json.dumps("{'message': '传入参数错误,请携带正确参数请求'}", ensure_ascii=False)
    return json.dumps("{'token': '未知错误'}", ensure_ascii=False)


# 用户注册函数
@app.route("/register", methods=["POST"])
def Register():
    if request.method == "POST":
        obtain_dict = request.form.to_dict()
        if len(obtain_dict) != 0 and len(obtain_dict) == 2:

            print("用户名: {} 密码: {}".format(obtain_dict["username"], obtain_dict["password"]))
            reg_username = obtain_dict["username"]
            reg_password = obtain_dict["password"]

            # 验证是否合法
            if CheckParameters(reg_username, reg_password) == False:
                return json.dumps("{'message': '传入用户名密码不合法'}", ensure_ascii=False)

            # 查询用户是否存在
            select = RunSqlite("database.db", "UserAuthDB", "select", "id", f"username='{reg_username}'")
            if select != []:
                return json.dumps("{'message': '用户名已被注册'}", ensure_ascii=False)
            else:
                insert = RunSqlite("database.db", "UserAuthDB", "insert", "username,password",
                                   f"'{reg_username}','{reg_password}'")
                if insert == True:
                    return json.dumps("{'message': '注册成功'}", ensure_ascii=False)
                else:
                    return json.dumps("{'message': '注册失败'}", ensure_ascii=False)
        else:
            return json.dumps("{'message': '传入参数个数不正确'}", ensure_ascii=False)
    return json.dumps("{'message': '未知错误'}", ensure_ascii=False)


# 密码修改函数
@app.route("/modify", methods=["POST"])
@login_check
def modify():
    if request.method == "POST":
        obtain_dict = request.form.to_dict()
        if len(obtain_dict) != 0 and len(obtain_dict) == 1:

            mdf_password = obtain_dict["password"]
            get_token = request.headers.get("token")
            print("获取token: {} 修改后密码: {}".format(get_token, mdf_password))

            # 验证是否合法
            if CheckParameters(get_token, mdf_password) == False:
                return json.dumps("{'message': '传入密码不合法'}", ensure_ascii=False)

            # 先得到token对应用户名
            select = RunSqlite("./database.db", "SessionAuthDB", "select", "username", f"token='{get_token}'")
            if select != []:
                # 接着直接修改密码即可
                modify_username = str(select[0][0])
                print("得到的用户名: {}".format(modify_username))
                update = RunSqlite("database.db", "UserAuthDB", "update", f"username='{modify_username}'",
                                   f"password='{mdf_password}'")
                if update == True:
                    # 删除原来的token,让用户重新获取
                    delete = RunSqlite("./database.db", "SessionAuthDB", "delete", f"username='{modify_username}'",
                                       "none")
                    print("删除token状态: {}".format(delete))
                    return json.dumps("{'message': '修改成功,请重新登录获取Token'}", ensure_ascii=False)

                else:
                    return json.dumps("{'message': '修改失败'}", ensure_ascii=False)
            else:
                return json.dumps("{'message': '不存在该Token,无法修改密码'}", ensure_ascii=False)
        else:
            return json.dumps("{'message': '传入参数个数不正确'}", ensure_ascii=False)
    return json.dumps("{'message': '未知错误'}", ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
