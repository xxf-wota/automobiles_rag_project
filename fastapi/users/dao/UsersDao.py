
from common import MySQLUtil
from users.entity.UsersEntity import UsersEntity

"""
    用于插入用户注册信息
    需要进行事务管理，确保数据的一致性
    如果插入失败，需要回滚事务
"""
def insert_user(usersEntity: UsersEntity):
    username = usersEntity.username
    password = usersEntity.password
    email = usersEntity.email
    # 连接MySQL数据库
    conn = MySQLUtil.get_mysql_conn()
    # 创建游标对象
    cursor = conn.cursor()
    try:
        # 编写sql语句
        sql = "INSERT INTO users VALUES (null, %s, %s, %s, now())"
        # 执行sql语句
        cursor.execute(sql, [username, email, password])
        # 提交事务
        conn.commit()
        print("插入用户成功")
        return "插入用户成功"
    except Exception as e:
        # 回滚事务
        conn.rollback()
        print(f"插入用户失败：{e}")
        return "插入用户失败"
    finally:
        # 关闭游标和连接
        MySQLUtil.close_mysql_conn(cursor, conn)


# 查询email对应的用户信息
def query_user_by_email(email: str):
    # 连接MySQL数据库
    conn = MySQLUtil.get_mysql_conn()
    # 创建游标对象
    cursor = conn.cursor()
    try:
        # 编写sql语句
        sql = "SELECT * FROM users WHERE email = %s"
        # 执行sql语句
        cursor.execute(sql, [email])
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和连接
        MySQLUtil.close_mysql_conn(cursor, conn)
        return result
    except Exception as e:
        print(f"查询用户失败：{e}")
        return None

# 通过user_id查询用户信息
def query_user_by_id(userId: int):
    conn = MySQLUtil.get_mysql_conn()
    # 创建游标对象
    cursor = conn.cursor()
    try:
        # 编写sql语句
        sql = "SELECT * FROM users WHERE user_id = %s"
        # 执行sql语句
        cursor.execute(sql, [userId])
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和连接
        MySQLUtil.close_mysql_conn(cursor, conn)
        return result
    except Exception as e:
        print(f"查询用户失败：{e}")
        return None

# 修改密码
def change_password(email: str, newPassword: str):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        sql = "UPDATE users SET password = %s WHERE email = %s"
        cursor.execute(sql, [newPassword, email])
        # 提交事务
        conn.commit()
        print("修改密码成功")
        return True
    except Exception as e:
        conn.rollback()
        print(f"修改密码失败：{e}")
        return False
    finally:
        MySQLUtil.close_mysql_conn(cursor, conn)






# 插入users_role表，记录用户角色
def insert_users_role(userId: int, username: str):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO users_role VALUES (%s, %s, 'user', now())"
        cursor.execute(sql, [userId, username])
        # 提交事务
        conn.commit()
        print("插入用户角色成功")
        return True
    except Exception as e:
        conn.rollback()
        print(f"插入用户角色失败：{e}")
        return False
    finally:
        MySQLUtil.close_mysql_conn(cursor, conn)


# 插入用户状态表，记录用户封禁状态，默认值为False表示未封禁（正常）
def insert_users_status(user_id: int, username: str, status: bool = False):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    # 有5个字段，分别是user_id, username, status, banned_time, normal_time
    try:
        sql = "INSERT INTO users_status VALUES (%s, %s, %s, now(), now())"
        cursor.execute(sql, [user_id, username, status])
        conn.commit()
        print("插入用户状态成功")
        return True
    except Exception as e:
        conn.rollback()
        print(f"插入用户状态失败：{e}")
        return False
    finally:
        MySQLUtil.close_mysql_conn(cursor, conn)







# 查询users_role表，根据用户ID查询用户角色
def query_users_role(userId: int):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        sql = "SELECT * FROM users_role WHERE user_id = %s"
        cursor.execute(sql, [userId])
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和连接
        MySQLUtil.close_mysql_conn(cursor, conn)
        return result
    except Exception as e:
        print(f"查询用户角色失败：{e}")
        return None

# 修改用户角色
def change_role(user_id: int, role: str):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        sql = "UPDATE users_role SET role = %s WHERE user_id = %s"
        cursor.execute(sql, [role, user_id])
        # 提交事务
        conn.commit()
        print("修改用户角色成功")
        return True
    except Exception as e:
        conn.rollback()
        print(f"修改用户角色失败：{e}")
        return False
    finally:
        MySQLUtil.close_mysql_conn(cursor, conn)



# 查询用户角色表
def get_user_role_list():
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        sql = "SELECT * FROM users_role WHERE role = 'user' or role = 'admin'"
        cursor.execute(sql)
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和连接
        MySQLUtil.close_mysql_conn(cursor, conn)
        return result
    except Exception as e:
        print(f"查询用户角色失败：{e}")
        return None


# 查询用户封禁状态
def get_user_ban_status():
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        sql = "SELECT * FROM users_status WHERE status = True or status = False"
        cursor.execute(sql)
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和连接
        MySQLUtil.close_mysql_conn(cursor, conn)
        return result
    except Exception as e:
        print(f"查询用户封禁状态失败：{e}")
        return None


# 用户封禁服务
def ban_user(userId, status, ban_time: int = 0):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        # ban_time 表示分钟
        sql = "UPDATE users_status SET status = %s, banned_time = now(), normal_time = now()+INTERVAL %s MINUTE WHERE user_id = %s"
        cursor.execute(sql, [status, ban_time, userId])
        # 提交事务
        conn.commit()
        print("修改用户封禁状态成功")
        return True
    except Exception as e:
        conn.rollback()
        print(f"修改用户封禁状态失败：{e}")
        return False
    finally:
        MySQLUtil.close_mysql_conn(cursor, conn)


# 根据用户ID查询用户封禁状态
def get_user_ban_status_by_user_id(user_id: int):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        sql = "SELECT * FROM users_status WHERE user_id = %s"
        cursor.execute(sql, [user_id])
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和连接
        MySQLUtil.close_mysql_conn(cursor, conn)
        return result
    except Exception as e:
        print(f"查询用户封禁状态失败：{e}")
        return None




if __name__ == '__main__':
    # insert_user(UsersEntity(username="test", password="123456", email="test@example.com"))
    # results = query_user_by_email("1359525405@qq.com")
    # print(results)
    # results = query_users_role(3)
    # print(results)
    # results = get_user_role_list()

    # results = ban_user(6, 0, 60)
    results = get_user_ban_status_by_user_id(3)
    print(results)


