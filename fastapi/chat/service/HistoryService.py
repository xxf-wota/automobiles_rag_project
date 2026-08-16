from chat.dao import HistoryDao


# 获取详细的历史记录
def conversation_log(historyId):
    # results = [{"question": ..., "answer": ...},{...}]
    results = HistoryDao.conversation_log(historyId)
    data_list = []
    # 将results转换为chat格式
    # [{"role": "user", "content": "你好"},
    # {"role": "assistant", "content": "你好，我是自动回复助手"}]
    for item in results:
        data_list.append({
            'role': 'user',
            'content': item['question']
        })
        data_list.append({
            'role': 'assistant',
            'content': item['answer']
        })
    return {
        "code": 200,
        "msg": "查询成功",
        "data": data_list
    }

# 获取历史记录列表
def query_history_menu(userId):
    # 通过user_id查询历史记录
    results = HistoryDao.query_history_menu(userId)
    # 包装成前端需要的格式
    data_list = []
    for item in results:
        data_list.append({
            'id': item['history_id'],
            'title': item['question'],
            'time': item['create_time'].strftime("%Y-%m-%d %H:%M:%S"),
        })
    return {
        "code": 200,
        "msg": "查询成功",
        "data": data_list
    }


# 删除指定的历史记录
def delete_conversation(historyId):
    results = HistoryDao.delete_conversation(historyId)
    if results:
        return {
            "code": 200,
            "msg": "删除成功",
            "data": None
        }
    else:
        return {
            "code": 400,
            "msg": "删除失败",
            "data": None
        }


# 搜索父级历史记录
def search_parent_history(userId, question):
    results=HistoryDao.search_parent_history(userId, question)
    # 进行包装
    data_list = []
    for item in results:
        data_list.append({
            'id': item['history_id'],
            'title': item['question'],
            'time': item['create_time'].strftime("%Y-%m-%d %H:%M:%S"),
        })
    return {
        "code": 200,
        "msg": "查询成功",
        "data": data_list
    }




if __name__ == '__main__':
    # print(conversation_log(1))
    # print(query_history_menu(3))
    print(search_parent_history(3, "你好"))
    print(len(search_parent_history(3, "你好")['data']))

