from langchain_core.messages import AIMessage, AIMessageChunk
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from ai import LoadLLM, LoadChroma, LoadRerankerModel
from chat.dao import ChatDao
from chat.entity.ConversationEntity import ConversationEntity
from chat.service import HistoryService
from chat.tools.ChatTool import query_neo4j
from chat.utils import IntentionUtil, BM25Util, RRFUtil
from common import RedisUtil, Neo4jUtil
import re
from users.dao import UsersDao
from langchain.agents import create_agent
from chat.tools import ChatTool
# 聊天服务
"""
    为了防止用户调用大模型使用过多次数的token，
    需要记录用户user_id，每次调用大模型时，需要判断用户user_id是否存在，若不存在则返回错误信息
    或存在则记录user_id调用次数，若次数超过阈值则返回错误信息
    
"""

# 上下文压缩配置
MAX_HISTORY_TOKENS = 4000       # 历史记录总 token 上限
KEEP_RECENT_ROUNDS = 3          # 保留最近 N 轮原始对话


def smart_compress_history(history, llm):
    """
        智能压缩历史对话上下文：
        1. 估算 token 总量，未超限则不压缩
        2. 超限时：对早期对话生成摘要，保留最近 N 轮原始对话
        3. 摘要以 system 消息形式注入，让模型理解历史背景
    """
    """
        虽然压缩了上下文，但是客户端显示的上下文内容不会改变，
        因为客户端显示的是mysql中的history表中的信息
    """

    if not history:
        return history

    # 估算 token 数（中文约 1 字符 ≈ 1 token，英文约 4 字符 ≈ 1 token，取折中 2 字符 ≈ 1 token）
    total_chars = sum(len(m['content']) for m in history)
    estimated_tokens = total_chars // 2
    print(f"此窗口的token为：{estimated_tokens}") # 方便看窗口下的还有多少超限
    # 还没到上限，直接返回
    if estimated_tokens <= MAX_HISTORY_TOKENS:
        return history

    # 保留最近 N 轮（每轮 = user + assistant，共 2 条）
    recent_count = KEEP_RECENT_ROUNDS * 2
    if len(history) <= recent_count:
        return history

    old_history = history[:-recent_count]
    recent_history = history[-recent_count:]

    # 格式化旧历史为文本
    old_text = ""
    for msg in old_history:
        role = "用户" if msg['role'] == 'user' else "助手"
        old_text += f"{role}: {msg['content']}\n"

    # 调用 LLM 生成摘要
    try:
        summary = llm.invoke(
            f"请用一段话总结以下对话的关键信息，包括用户意图、重要事实和决策：\n{old_text}"
        ).content
        compressed = [
            {"role": "system", "content": f"【历史对话摘要】{summary}"}
        ] + recent_history
        print(f"上下文压缩完成：原始 {len(history)} 条消息 → 压缩后 {len(compressed)} 条（摘要 + 最近 {KEEP_RECENT_ROUNDS} 轮）")
        return compressed
    except Exception as e:
        print(f"上下文压缩失败，降级为滑动窗口截断: {e}")
        return history[-recent_count:]


def chat(question, userId, historyId, request=None, llm=None, vector=None, bm25=None, docs=None, reranker=None):
    """
        参数说明：
            llm      - 从 app.state.llm 传入的预加载大模型
            vector   - 从 app.state.vector 传入的预加载向量数据库
            bm25     - 从 app.state.bm25 传入的预加载 BM25 索引
            docs     - 从 app.state.docs 传入的文档列表
            reranker - 从 app.state.reranker 传入的预加载重排序模型
    """


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
        history = HistoryService.conversation_log(historyId, userId)["data"]
    # print(history)
    # print(historyId)

    # 调用大模型对象
    # llm = LoadLLM.load_llm()
    domain = IntentionUtil.intention_recognition(request, question)["domain"]
    print(f"用户聊天的类型是：{domain}")

    # 智能压缩历史上下文，防止 token 超限
    history = smart_compress_history(history, llm)

    # domain有三个返回值分别是"auto" | "medical" | "chat"
    if domain == "chat":
        history.append({'role': 'user', 'content': question})
        # 直接用大模型回答问题
        # 将历史记录传入大模型，作为上下文信息
        # 使其能够根据历史记录回答用户问题
        for chunk in llm.stream(history):
            # 过滤掉空内容
            if chunk.content:
                print(chunk.content)
                yield chunk.content
        return

    elif domain == "medical" or domain == "weather":
        # 使用agent回答医疗健康相关问题
        agent = create_agent(
            model=llm,
            tools=[ChatTool.query_neo4j, ChatTool.get_weather],
            system_prompt="""
                你是一个智能助手，拥有两个专业工具可以帮助用户解决问题。你需要根据用户的问题，选择合适的工具来提供帮助。
                
                ## 你的身份
                你是一个多领域智能助手，可以处理医疗健康和天气查询两大类问题。
                
                ---
                
                ## 可用工具
                
                ### 工具1：`query_neo4j`（医疗知识库查询）
                **用途**：查询医疗健康相关的专业知识
                
                **适用场景**（遇到以下情况必须使用此工具）：
                - 疾病相关问题：感冒、发烧、高血压、糖尿病、心脏病、肺炎、癌症等
                - 症状咨询：头痛、咳嗽、头晕、恶心、疼痛、发热、呕吐、乏力等
                - 药品信息：用法用量、副作用、禁忌症、药物相互作用等
                - 诊疗方案：检查项目、治疗方案、手术信息等
                - 医学概念：生理指标、营养保健、病理机制等
                - 就医指导：科室推荐、就医流程等
                - 用户描述自身症状："我最近总是..."、"我有XX病..."
                
                **判断关键词**：
                疾病类：感冒、发烧、高血压、糖尿病、心脏病、肺炎、癌症、胃炎、肝炎、肾炎、关节炎
                症状类：头痛、咳嗽、头晕、恶心、疼痛、发热、呕吐、腹泻、便秘、失眠
                药物类：药、药品、阿莫西林、头孢、青霉素、胰岛素、抗生素、降压药
                身体部位：心脏、肝脏、胃、肺、脑、血管、骨骼、肌肉、神经、皮肤
                医疗行为：治疗、诊断、检查、手术、住院、吃药、打针、输液、体检
                
                ---
                
                ### 工具2：`get_weather`（天气查询）
                **用途**：查询实时天气和天气预报
                
                **适用场景**（遇到以下情况必须使用此工具）：
                - 查询当前天气状况
                - 查询未来天气预报（今天、明天、本周、周末等）
                - 查询特定城市的天气
                - 询问温度、降雨、降雪、风力、空气质量等
                - 询问是否需要带伞、穿衣建议等
                
                **判断关键词**：
                天气状况：天气、下雨、下雪、晴天、多云、阴天、刮风、台风
                温度相关：温度、气温、热、冷、暖和、凉快、降温、升温
                降水相关：降雨、降水量、暴雨、大雨、小雨、阵雨
                其他：雾霾、空气质量、紫外线、湿度、风力、天气预报
                
                ---
                
                ## 工具选择规则（优先级从高到低）
                
                ### 规则1：明确领域判断
                - 问题明确涉及医疗健康 → 使用 `query_neo4j`
                - 问题明确涉及天气查询 → 使用 `get_weather`
                - 问题明确与两者无关 → 不调用工具，直接聊天
                
                ### 规则2：关键词优先
                - 出现医疗关键词 → 使用 `query_neo4j`
                - 出现天气关键词 → 使用 `get_weather`
                
                ### 规则3：安全优先（医疗优先）
                - 当问题同时涉及医疗和天气（如"天冷容易感冒吗"）→ 使用 `query_neo4j`
                - 当问题同时涉及医疗和汽车（如"开车时头晕"）→ 使用 `query_neo4j`
                - **医疗问题永远优先于天气问题**
                
                ### 规则4：模糊问题处理
                - "今天适合出去玩吗" → 可能隐含天气查询，但不够明确 → 追问用户是否想查天气
                - "天气冷会生病吗" → 涉及医疗和天气 → 医疗优先，使用 `query_neo4j`
                
                ### 规则5：不调用工具的场景
                - 日常问候："你好"、"早上好"、"吃了没"
                - 纯闲聊："讲个笑话"、"今天心情不好"
                - 询问助手本身："你叫什么名字"、"你能做什么"
                - 与医疗和天气都无关的话题
                
                ---
                
                ## 典型场景示例
                
                | 用户问题 | 应该使用的工具 | 判断理由 |
                |---------|--------------|---------|
                | "感冒了吃什么药" | query_neo4j | 包含疾病"感冒"和"药" |
                | "今天北京天气怎么样" | get_weather | 明确查询天气 |
                | "头痛是什么原因" | query_neo4j | 包含症状"头痛" |
                | "明天会下雨吗" | get_weather | 天气预报查询 |
                | "高血压需要注意什么" | query_neo4j | 包含疾病"高血压" |
                | "现在外面热吗" | get_weather | 询问温度 |
                | "开车时头晕怎么办" | query_neo4j | 涉及症状，医疗优先 |
                | "天冷容易感冒吗" | query_neo4j | 涉及医疗，医疗优先 |
                | "你好" | 不调用工具 | 日常问候 |
                | "今天适合出去玩吗" | 追问或get_weather | 隐含天气需求 |
                
                ---
                
                ## 工作流程
                
                ### 步骤1：分析用户问题
                - 提取关键词
                - 判断属于哪个领域
                
                ### 步骤2：选择工具
                - 根据上述规则决定使用哪个工具
                - 如果不属于任何领域，直接回复
                
                ### 步骤3：调用工具
                - 构造合适的参数
                - 执行工具调用
                
                ### 步骤4：处理结果
                
                #### 如果调用了 `query_neo4j`：
                1. 将返回的原始数据转化为自然、流畅的语言
                2. 按逻辑组织信息（病因→症状→治疗→预防）
                3. 药品信息必须包含：名称、适应症、副作用、注意事项
                4. 疾病信息必须包含：定义、症状、原因、就医建议
                5. **必须添加免责声明**："*以上信息仅供参考，不能替代专业医生的诊断和治疗建议，如有不适请及时就医。*"
                6. 如果无结果，如实告知并建议咨询医生
                
                #### 如果调用了 `get_weather`：
                1. 清晰展示天气信息
                2. 包含：温度、天气状况、降水概率、风力、空气质量等
                3. 如果有用信息（如"建议带伞"），主动提醒
                4. 语言自然友好
                
                #### 如果工具调用失败：
                1. 告知用户技术问题
                2. 建议稍后重试
                3. 不要猜测或编造答案
                
                ---
                
                ## 重要约束
                
                1. **每次对话只调用一个工具**（要么医疗，要么天气，不能同时调两个）
                2. **医疗问题必须调用工具**，不能凭记忆或推测回答
                3. **禁止提供医疗诊断**，所有医疗信息仅供参考
                4. **识别紧急情况**（胸痛、呼吸困难等），立即建议就医
                5. 对于模糊问题，主动追问澄清
                
                ---
                
                ## 示例对话
                
                ### 示例1：医疗问题 → 调用医疗工具
                用户："感冒了吃什么药好得快？"
                思考：包含"感冒"和"药" → 医疗问题 → 使用 query_neo4j
                助手：[调用 query_neo4j 查询"感冒 治疗 药物"]
                [返回结构化医疗信息 + 免责声明]
                
                ### 示例2：天气问题 → 调用天气工具
                用户："今天会下雨吗？"
                思考：包含"下雨" → 天气问题 → 使用 get_weather
                助手：[调用 get_weather 查询今天天气]
                [返回天气信息："今天多云，下午有小雨，降水概率60%，建议带伞"]
                
                ### 示例3：非工具问题 → 直接回复
                用户："你好"
                思考：日常问候 → 不调用工具
                助手："您好！我是智能助手，可以帮您查询医疗健康知识或天气信息，请问有什么可以帮您？"
                
                ### 示例4：边界问题 → 医疗优先
                用户："天冷会感冒吗？"
                思考：涉及"天冷"和"感冒" → 医疗优先 → 使用 query_neo4j
                助手：[调用 query_neo4j 查询"感冒 诱因 寒冷"]
                [返回：寒冷天气与感冒的关系 + 预防建议 + 免责声明]
                
                ### 示例5：模糊问题 → 追问
                用户："今天适合出去玩吗？"
                思考：可能隐含天气需求，但不够明确
                助手："您是想了解今天的天气情况吗？我可以帮您查询天气。或者您有其他问题？"
                
                ### 示例6：紧急情况 → 立即建议就医
                用户："我胸痛怎么办？"
                思考：包含"胸痛"，可能紧急 → 立即建议就医
                助手："⚠️ 胸痛可能是严重疾病的信号，请立即前往医院急诊科就诊，或拨打急救电话！不要拖延！"
                
                ---
                
                现在请根据用户的输入，选择合适的工具来提供帮助。
                """,
            debug=True,
        )
        # 添加记忆
        history.append({'role': 'user', 'content': question})
        messages = []
        document = ''
        for chunk, metadata in agent.stream(
            {"messages": history}, # 由于history已经是消息格式，所以直接传递
            stream_mode="messages", # 流式输出，以token的形式传递
        ):
            # 流式输出需要AIMessageChunk适配
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                document += chunk.content
                yield chunk.content
            # 代表完整的消息对象（非流式输出）
            elif isinstance(chunk, AIMessage) and chunk.content:
                messages.append(chunk)
        print(document)


    elif domain == "auto":

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
        # 调用向量数据库对象
        # vector = LoadChroma.load_Chroma_conn()

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
            # bm25, docs = BM25Util.build_bm25_index(vector_result)
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

            # 调用重排序模型对象
            # reranker = LoadRerankerModel.load_reranker_model()

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

# 关于普通聊天的回答
def normal_chat(question, userId, historyId, llm=None):
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
        history = HistoryService.conversation_log(historyId, userId)["data"]
    # 调用大模型对象
    # llm = LoadLLM.load_llm()
    domain = IntentionUtil.intention_recognition(question)["domain"]
    print(f"用户聊天的类型是：{domain}")
    # domain有三个返回值分别是"auto" | "medical" | "chat"
    if domain == "chat":
        history.append({'role': 'user', 'content': question})
        # 直接用大模型回答问题
        # 将历史记录传入大模型，作为上下文信息
        # 使其能够根据历史记录回答用户问题
        for chunk in llm.stream(history):
            # 过滤掉空内容
            if chunk.content:
                print(chunk.content)
                yield chunk.content
        return








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
    question = "头晕怎么办"
    user_id = 3
    historyId = 0
    for chunk in chat(question, user_id, historyId, llm=LoadLLM.load_llm()):
        print(chunk)