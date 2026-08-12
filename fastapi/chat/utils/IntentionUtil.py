import json
import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_ollama import ChatOllama


load_dotenv()

# 意图识别函数
def intention_recognition(question: str):
    # 初始化Ollama模型
    ollama = ChatOllama(
        model=os.getenv("OLLAMA_MODEL_NAME"),
        base_url=os.getenv("OLLAMA_BASE_URL"),
    )

    # 提示词文本内容
    intention_prompt = """
        你是一个汽车领域意图识别助手。你的任务是判断用户输入是否属于“回答汽车相关问题”的意图，并将其归类到指定类别中。

        请仅根据用户输入内容进行判断，不要编造车辆信息，也不要直接回答汽车问题。
        
        ### 判断范围
        “汽车问题”包括但不限于：
        - 汽车故障诊断
        - 仪表盘故障灯含义
        - 发动机、变速箱、底盘、刹车、轮胎、电瓶等部件问题
        - 保养周期、机油、滤芯、刹车片等养护问题
        - 购车、选车、车型对比、配置解读
        - 油耗、续航、充电、加油相关问题
        - 驾驶操作、安全配置、车机系统使用
        - 保险、年检、上牌、违章、二手车等用车相关问题
        
        ### 输出类别
        请从以下类别中选择一个：
        
        1. 汽车故障诊断
        2. 汽车保养维修
        3. 购车选车咨询
        4. 驾驶与用车操作
        5. 车辆配置与功能说明
        6. 汽车政策与手续
        7. 非汽车问题
        8. 意图不明确
        
        ### 输出格式
        严格按以下 JSON 格式输出，不要输出额外解释：
        
        {
            "is_car_question": true or false,
            "intent": "意图类别",
            "confidence": "高/中/低",
            "reason": "一句话判断理由"
        }
        
        ### 判断规则
        - 如果用户输入明确与汽车、车辆、驾驶、保养、故障、购车、用车相关，则 is_car_question 为 true。
        - 如果用户输入与汽车无关，则 is_car_question 为 false，intent 为“非汽车问题”。
        - 如果用户输入信息不足，无法确定具体汽车意图，则 intent 为“意图不明确”。
        - confidence 表示判断置信度：
            - 高：问题明确且关键词清晰
            - 中：问题相关但表述模糊
            - 低：信息不足或存在歧义
    """
    # 输出的结果有一个参数is_car_question，用于判断用户输入是否属于“回答汽车相关问题”的意图
    res = ollama.invoke([
        # 系统提示词
        {"role": "system", "content": intention_prompt},
        # 用户问题
        {"role": "user", "content": question}
    ])
    # print(type(res.content)) # <class 'str'>
    # print(res.content)


    return json.loads(res.content)



if __name__ == '__main__':
    result = intention_recognition("你好")
    print(result)
