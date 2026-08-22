from langchain_neo4j import Neo4jGraph
import os
from dotenv import load_dotenv
load_dotenv()
# 连接neo4j数据库
def get_neo4j_graph():
    return Neo4jGraph(
        url=os.getenv("NEO4J_URL"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        database=os.getenv("NEO4J_DATABASE"),
    )

if __name__ == '__main__':
    graph = get_neo4j_graph()
    print(graph)