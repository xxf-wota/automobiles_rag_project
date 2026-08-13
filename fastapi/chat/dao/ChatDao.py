from common import MySQLUtil


def save_conversation(question, user_id, parentId, answer):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        sql = "insert into history values(null, %s, %s, %s, %s, now())"
        cursor.execute(sql, [question, user_id, parentId, answer])
        print("新增聊天记录成功")
        conn.commit()
        # 将主键自增id返回
        return cursor.lastrowid
    except Exception as e:
        print(f"新增聊天记录失败：{e}")
        conn.rollback()
        return 0
    finally:
        MySQLUtil.close_mysql_conn(cursor, conn)


if __name__ == '__main__':
    question = "你好"
    user_id = 3
    conversation_id = save_conversation(question, user_id, 1, "你好，我是AI助手")
