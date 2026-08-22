from pydantic import BaseModel, Field


class ConversationEntity(BaseModel):
    question: str = Field(..., description="用户问题")
    userId: int = Field(..., description="用户id")
    # 父级id，首次调用时为0，后续调用时为父级记录的id
    # 用于实现对话的连续性
    parentId: int = Field(..., description="父级id")
    answer: str = Field(..., description="答案")


class Neo4jEntity(BaseModel):
    cql: str = Field(..., description="CQL语句")


class WeatherEntity(BaseModel):
    city: str = Field(..., description="城市名称")
