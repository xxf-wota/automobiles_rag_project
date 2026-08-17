from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from ai import LoadLLM, LoadChroma, LoadRerankerModel
from chat.dao import ChatDao
from chat.entity.ConversationEntity import ConversationEntity
from chat.service import HistoryService
from chat.utils import IntentionUtil, BM25Util, RRFUtil
from common import RedisUtil

from users.dao import UsersDao

# 聊天服务
"""
    为了防止用户调用大模型使用过多次数的token，
    需要记录用户user_id，每次调用大模型时，需要判断用户user_id是否存在，若不存在则返回错误信息
    或存在则记录user_id调用次数，若次数超过阈值则返回错误信息
    
"""
def chat(question, userId, historyId):


    """
        验证用户user_id是否存在
        防止用户直接跳转到聊天服务没有通过登录验证
    """
    # 在这个函数中mysql已经进行了连接和关闭，所以不需要再连接
    user_data = UsersDao.query_user_by_id(userId)
    # 若用户user_id不存在，则返回错误信息
    if not user_data:
        return {
            "code": 400,
            "msg": "用户不存在,请先登录",
            "data": None
        }

    # 判断historyId是否为0，表示新对话的开始
    if historyId == 0:
        # 新对话的开始，将历史记录清空
        history = []
    else:
        # 得到的是chat格式的历史记录
        history = HistoryService.conversation_log(historyId)["data"]
    # print(history)
    # print(historyId)

    # 调用大模型对象
    llm = LoadLLM.load_llm()
    is_car_question = IntentionUtil.intention_recognition(question)["is_car_question"]
    print(is_car_question)
    # 若is_car_question为True，则调用RAG检索方法
    if not is_car_question:
        history.append({'role': 'user','content': question})
        # 直接用大模型回答问题
        # 将历史记录传入大模型，作为上下文信息
        # 使其能够根据历史记录回答用户问题
        for chunk in llm.stream(history):
            # 过滤掉空内容
            if chunk.content:
                print(chunk.content)
                yield chunk.content
        return

    # 意图识别为True，所以需要调用RAG检索方法
    # 提示词
    template = """
        你是一个基于知识库的AI助手。请根据RAG检索内容回答用户问题。
        规则：
            - 仅基于提供的知识回答，不使用外部知识补充。
            - 检索内容不足时，说明信息不足，不要猜测。
            - 优先提炼关键答案，避免冗长解释。
            - 保持回答自然、简洁、有帮助。
            - 输出结果的时候，不允许输出根据提供的参考资料这样的内容
            - 输出结果的时候，如果没有参考的上下文信息，请给出一个友好的回复信息
            
        历史记录：
            {history}
        参考资料：
            {context}
        问题：
            {question}
        答案：
    """
    # 构建提示词对象
    prompt = PromptTemplate(
        template=template,
        input_variables=["history", "context", "question"]
    )

    # 加载向量数据库对象
    vector = LoadChroma.load_Chroma_conn()

    # 获取向量检索器
    retriever = vector.as_retriever(search_kwargs={"k": 20})

    # 打印召回的文档
    def print_recall(title, docs):
        print(f"{title}到的文档：")
        print(docs)
        for doc in docs:
            print(doc.page_content)
            print('=' * 100)
        return docs # 返回召回的文档

    # 混合检索
    def retriever_func():
        # 向量检索
        vector_result = retriever.invoke(question)
        print_recall("向量检索", vector_result)
        # BM25检索
        bm25, docs = BM25Util.build_bm25_index(vector)
        bm25_results = BM25Util.bm25_retriever(bm25, question, docs, k=20)
        print_recall("BM25检索", bm25_results)

        # rrf融合
        result = RRFUtil.rrf(vector_result, bm25_results)

        return result




       # 重排序
    def reranker_func(data):
        print("开始进行重排序：")
        print(data)
        # 将召回的文档核问题提取出来
        history = data["history"]
        docs = data["context"]
        question = data["question"]

        # 将文档内容打包成列表
        doc_list = [doc.page_content for doc in docs]
        print(doc_list)

        # 加载重排序模型
        reranker = LoadRerankerModel.load_reranker_model()
        # 设置重排序后的文档数据为15个
        top_k = 15
        # 将问题和文档用元组打包，为了调用重排序的计算方法
        reranker_list = [(question, doc) for doc in doc_list]
        # 调用计算方法
        scores = reranker.compute_score(reranker_list)
        print(scores)
        # 将分数和文档内容打包，并排序
        sorted_scores = sorted(zip(scores, doc_list), key=lambda x: x[0], reverse=True)
        # 取top_k个文档
        top_k_docs = [doc for score, doc in sorted_scores[:top_k]]
        print("重排序后的文档：")
        for index, doc in enumerate(top_k_docs):
            print(f"查询到的文档{index + 1}： {doc}")
            print('=' * 100)

        # 还需要将文档提取出来用于返回
        doc = [doc for doc in top_k_docs]
        return {
            "history": history,
            "context": doc,
            "question": question,
        }


    # 构建chain
    qa_chain = (
        RunnableParallel(
            {
                "history": RunnableLambda(lambda _: history),
                "context": RunnableLambda(lambda _: retriever_func()),
                "question": RunnablePassthrough(), # 保持用户问题不变
            }
        )
        | RunnableLambda(reranker_func)
        | prompt
        | llm
        | StrOutputParser()
    )
    for chunk in qa_chain.stream(question):
        # 过滤掉空内容
        if chunk:
            print(chunk)
            yield chunk


# 保存聊天记录
def save_conversation(conversationEntity: ConversationEntity):
    # 从conversationEntity中提取数据
    question = conversationEntity.question
    user_id = conversationEntity.userId
    parentId = conversationEntity.parentId
    answer = conversationEntity.answer
    # 保存聊天记录
    history_id = ChatDao.save_conversation(question, user_id, parentId, answer)
    if history_id != 0:
        return {
            "code": 200,
            "msg": "新增聊天记录成功",
            "data": {
                "history_id": history_id
            }
        }
    else:
        return {
            "code": 400,
            "msg": "新增聊天记录失败",
            "data": None
        }






if __name__ == '__main__':
    question = "宝马1系 2018款官方指导价"
    user_id = 3
    # print(list(chat(question, user_id)))