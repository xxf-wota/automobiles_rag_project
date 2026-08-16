from common import MySQLUtil

# 获取详细的历史记录
def conversation_log(historyId):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    # 通过history_id和parent_id查询问题和答案并按history_id升序排序，即按时间顺序排序
    sql = "select question, answer from history where history_id = %s or parent_id = %s order by history_id ASC"
    cursor.execute(sql, [historyId, historyId])
    results = cursor.fetchall()
    MySQLUtil.close_mysql_conn(cursor, conn)
    return results




# 获取历史记录列表
def query_history_menu(userId):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    # 通过user_id查询历史记录
    sql = "select history_id, question, create_time from history where user_id = %s  and parent_id = 0"
    cursor.execute(sql, [userId])
    results = cursor.fetchall()
    MySQLUtil.close_mysql_conn(cursor, conn)
    return results

# 删除指定的历史记录
def delete_conversation(historyId):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    try:
        # 删除父记录和子记录
        sql = "delete from history where history_id = %s or parent_id = %s"
        cursor.execute(sql, [historyId, historyId])
        conn.commit()
        return True
    except Exception as e:
        conn.rollback() # 失败时回滚事务
        return False
    finally:
        MySQLUtil.close_mysql_conn(cursor, conn)


# 搜索父级历史记录
def search_parent_history(userId, question):
    conn = MySQLUtil.get_mysql_conn()
    cursor = conn.cursor()
    # 通过parent_id查询父记录
    sql = "select history_id, question, create_time from history where user_id = %s and question like %s and parent_id = 0"
    cursor.execute(sql, [userId, f"%{question}%"])
    results = cursor.fetchall()
    MySQLUtil.close_mysql_conn(cursor, conn)
    return results





if __name__ == '__main__':
    # print(conversation_log(1))
    # print(query_history_menu(3))
    print(search_parent_history(3, "车内"))


