# MySQL数据库工具类
import pymysql

import os
from dotenv import load_dotenv

load_dotenv()

# 连接MySQL数据库
def get_mysql_conn():
    return pymysql.connect(
        # 数据库主机地址
        host=os.getenv("MYSQL_HOST"),
        # 数据库端口号
        port=int(os.getenv("MYSQL_PORT")),
        # 数据库用户名
        user=os.getenv("MYSQL_USER"),
        # 数据库密码
        password=os.getenv("MYSQL_PASSWORD"),
        # 数据库名称
        database=os.getenv("MYSQL_DATABASE"),
        # 数据库字符集
        charset=os.getenv("MYSQL_CHARSET"),
        # 数据库游标类型
        # 以字典形式返回查询结果集 [{}]，而不是 ((),)
        cursorclass=pymysql.cursors.DictCursor
    )

# 关闭MySQL数据库连接
def close_mysql_conn(cursor, conn):
    cursor.close()
    conn.close()
