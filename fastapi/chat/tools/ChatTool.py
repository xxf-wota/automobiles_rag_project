import os

from langchain_core.tools import tool

from common import Neo4jUtil
from chat.entity import ConversationEntity
import requests

# 连接neo4j数据库
graph = Neo4jUtil.get_neo4j_graph()

# 医疗相关的工具
@tool(
    name_or_callable="query_neo4j",
    description="""
        Task:Generate Cypher statement to query a graph database.
        Instructions:
        Use only the provided relationship types and properties in the schema.
        Do not use any other relationship types or properties that are not provided.
        数据库的信息定义如下：
        # 节点标签及含义
        | 节点标签     | 含义             |
        |--------------|------------------|
        | Disease      | 疾病（核心节点） |
        | Symptom      | 症状             |
        | Check        | 检查项目         |
        | Cureway      | 治疗方式         |
        | Drug         | 药物             |
        | Department   | 就诊科室         |
        | Food         | 食物             |
        | Dishes       | 菜肴             |
        | Category     | 疾病分类         |

        # 关系类型及含义
        | 关系类型             | 含义              | 起始节点 | 目标节点    |
        |----------------------|-------------------|----------|-------------|
        | DISEASE_SYMPTOM      | 疾病症状          | Disease  | Symptom     |
        | DISEASE_CHECK        | 相关检查项目      | Disease  | Check       |
        | DISEASE_CUREWAY      | 治疗方式          | Disease  | Cureway     |
        | DISEASE_DRUG         | 治疗或相关药物    | Disease  | Drug        |
        | DISEASE_DEPARTMENT   | 就诊科室          | Disease  | Department  |
        | DISEASE_DO_EAT       | 推荐进食的食物    | Disease  | Food        |
        | DISEASE_NOT_EAT      | 不推荐进食的食物  | Disease  | Food        |
        | DISEASE_DISHES       | 适合疾病的菜肴    | Disease  | Dishes      |
        | DISEASE_ACOMPANY     | 并发症 / 伴随疾病 | Disease  | Disease     |
        | DISEASE_CATEGORY     | 疾病所属类别      | Disease  | Category    |

        # 查询示例
        # 问：高血压有哪些症状？
        MATCH (d:Disease {{name:"高血压"}})-[:DISEASE_SYMPTOM]->(s:Symptom) RETURN s.name AS symptom

        # 问：感冒吃什么药？
        MATCH (d:Disease {{name:"感冒"}})-[:DISEASE_DRUG]->(dr:Drug) RETURN dr.name AS drug

        # 问：糖尿病不宜吃什么？
        MATCH (d:Disease {{name:"糖尿病"}})-[:DISEASE_NOT_EAT]->(f:Food) RETURN f.name AS food

        # 问：肺炎需要做什么检查？
        MATCH (d:Disease {{name:"肺炎"}})-[:DISEASE_CHECK]->(c:Check) RETURN c.name AS check_item

        # 问：高血压挂什么科？
        MATCH (d:Disease {{name:"高血压"}})-[:DISEASE_DEPARTMENT]->(dep:Department) RETURN dep.name AS department

        # 问：感冒的并发症有哪些？
        MATCH (d:Disease {{name:"感冒"}})-[:DISEASE_ACOMPANY]->(a:Disease) RETURN a.name AS complication

        # 问：糖尿病属于哪类疾病？
        MATCH (d:Disease {{name:"糖尿病"}})-[:DISEASE_CATEGORY]->(c:Category) RETURN c.name AS category

        # 问：高血压可以吃什么菜？
        MATCH (d:Disease {{name:"高血压"}})-[:DISEASE_DISHES]->(dishes:Dishes) RETURN dishes.name AS dishes

        # 问：哪些疾病会有头痛症状？
        MATCH (d:Disease)-[:DISEASE_SYMPTOM]->(s:Symptom {{name:"头痛"}}) RETURN d.name AS disease

        Note: Do not include any explanations or apologies in your responses.
        Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
        Do not include any text except the generated Cypher statement.

        参数：
            cql: 查询命令
    """,
    args_schema=ConversationEntity.Neo4jEntity,  # 参数校验
)
def query_neo4j(cql: str) -> dict:
    result = graph.query(cql)
    print(f"得到的相关结果：{result}")

    return {
        "result": result  # 使用query()查询到的就是结果，不需要再.data()
    }

# 查询天气的工具
@tool(
    name_or_callable="get_weather",
    description="""
        当用户需要查询某个城市的天气时，调用此工具
        参数：
            city：字符串类型，表示城市名称
    """,
    args_schema=ConversationEntity.WeatherEntity, # 参数校验
)
def get_weather(city: str) -> dict:
    print(f"查询{city}的天气")
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params ={
        "key": os.getenv("GAODE_API_KEY"),
        "city": city,
    }
    response = requests.get(url, params=params)
    result = response.json() # 获取请求后的json数据
    # 拼接天气数据
    live = result["lives"][0]
    return {
        "result": (
            f"{live['province']}{live['city']}当前天气{live['weather']}，"
            f"气温{live['temperature_float']}℃，湿度{live['humidity_float']}%，"
            f"{live['winddirection']}风{live['windpower']}级，"
            f"数据更新时间为{live['reporttime']}。"
        )
    }







