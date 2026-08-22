import json
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import Request
from langchain_ollama import ChatOllama


load_dotenv()

# 意图识别函数
def intention_recognition(request: Optional[Request], question: str, ollama: Optional[ChatOllama] = None):
    # 初始化Ollama模型
    if ollama is None:
        ollama = request.app.state.ollama

    # 提示词文本内容
    intention_prompt = """
        你是一个专业的意图识别助手。你的任务是将用户的问题分类到以下四个领域之一：
        
        **领域说明：**
        
        1. **auto（汽车领域）**：关于汽车的一切问题
           - 车辆部件：发动机、变速箱、刹车、轮胎、方向盘、电瓶、机油等
           - 车辆类型：轿车、SUV、新能源车、电动车、混动车等
           - 汽车品牌：特斯拉、比亚迪、蔚来、小鹏、理想、奔驰、宝马、奥迪等
           - 驾驶相关：油耗、续航、充电、保养、维修、故障、异响、驾驶、导航等
           - 购车相关：价格、配置、性价比、试驾等
        
        2. **medical（医疗领域）**：关于医疗健康的所有问题
           - 疾病名称：感冒、发烧、高血压、糖尿病、心脏病、肺炎、癌症等
           - 症状表现：头痛、咳嗽、头晕、恶心、疼痛、发热、呕吐等
           - 药物相关：药品、抗生素、阿莫西林、胰岛素、中药、西药等
           - 医疗行为：治疗、诊断、检查、手术、住院、吃药、体检等
           - 身体部位：心脏、肝脏、胃、肺、脑、血管等
           - 科室：内科、外科、儿科、妇科、骨科等
        
        3. **weather（天气领域）**：关于天气的所有查询
           - 天气状况：晴天、下雨、多云、刮风、下雪、温度、湿度、空气质量等
           - 天气预报：今天天气、明天天气、本周天气、周末天气等
           - 天气相关：气温、降雨、降雪、台风、雾霾、紫外线等
           - 询问方式：天气怎么样、热吗、冷吗、会不会下雨、需要带伞吗等
        
        4. **chat（闲聊）**：与医疗、汽车、天气无关的日常对话
           - 日常问候：你好、嗨、再见
           - 生活话题：心情、笑话、故事、美食、旅游等
           - 无意义对话：测试、随便聊聊
        
        **重要规则（优先级从高到低）：**
        
        1. **安全优先原则**：当用户同时提到汽车和医疗（如"开车时头晕"），优先判定为 **medical**
        2. **天气优先原则**：当用户明确询问天气状况，包括问"热吗""冷吗""下雨吗"等，判定为 **weather**
        3. **症状优先原则**：当问题涉及疾病症状、身体不适、药物治疗等，必须判定为 **medical**
        4. **明确领域判断**：只有当问题明确属于某一领域时，才分类到该领域
        5. **模糊问题处理**：如果问题模糊但提到身体部位或不适，倾向判为 medical
        
        **常见场景示例：**
        
        | 用户问题 | 正确分类 | 原因 |
        |---------|---------|------|
        | "今天天气怎么样" | weather | 明确询问天气 |
        | "明天会下雨吗" | weather | 天气预报查询 |
        | "北京天气热吗" | weather | 天气状况询问 |
        | "开车时头晕怎么办" | medical | 涉及身体不适，安全优先 |
        | "感冒了能开车吗" | medical | 涉及疾病，医疗优先 |
        | "特斯拉续航多少" | auto | 明确汽车问题 |
        | "你好" | chat | 日常问候 |
        | "今天适合出去玩吗" | chat | 不明确，无具体领域 |
        | "天气冷会影响汽车启动吗" | auto | 虽然提到天气，但核心是汽车问题 |
        | "下雨天开车注意什么" | auto | 核心是驾驶安全，不是天气查询 |
        
        **输出格式要求：**
        你必须以严格的JSON格式输出，不要包含任何其他文字，格式如下：
        {
            "domain": "auto" | "medical" | "weather" | "chat",
            "confidence": 0.0-1.0,
            "reason": "简短的中文说明，解释为什么这样分类"
        }
        
        现在请对用户的问题进行分类。
    """
    # 输出的结果有一个参数domain，用于判断用户输入是关于什么的
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
    from ai.LoadOllama import load_ollama
    result = intention_recognition(None, "我头晕怎么办", ollama=load_ollama())
    domain = result["domain"]
    print(domain)
    print(result)