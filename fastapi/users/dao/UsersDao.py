
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
def query_user_by_id(user_id: int):
    conn = MySQLUtil.get_mysql_conn()
    # 创建游标对象
    cursor = conn.cursor()
    try:
        # 编写sql语句
        sql = "SELECT * FROM users WHERE user_id = %s"
        # 执行sql语句
        cursor.execute(sql, [user_id])
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和连接
        MySQLUtil.close_mysql_conn(cursor, conn)
        return result
    except Exception as e:
        print(f"查询用户失败：{e}")
        return None




if __name__ == '__main__':
    # insert_user(UsersEntity(username="test", password="123456", email="test@example.com"))
    results = query_user_by_email("1359525405@qq.com")
    print(results)

