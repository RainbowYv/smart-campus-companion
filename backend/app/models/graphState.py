from typing import TypedDict, Annotated, List, Optional, Dict, Any, Union, Literal

from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


# 定义用户画像结构 (为后续个性化做准备)
class UserProfile(TypedDict):
    uid: int  # 数据库ID (student_id 或 teacher_id)
    role: str  # "student" | "teacher" | "admin"
    name: str  # 显示名称
    number: str  # 学号或者教师编号
    preferences: Dict  # {"notify_time": "morning", "theme": "dark"}


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

    # 2. 上下文层 (Context Layer)
    # 当前对话的用户是谁？从 API Gateway 传入，贯穿全流程
    user_info: UserProfile
    # 当前的时间、地点 (对 RAG 查讲座很重要)
    environment: Dict[str, Any]  # {"now": datetime, "location": "library"}

    structured_data: Optional[Dict[str, Any]]  # 工具原数据
    interrupt_data: Optional[Dict[str, Any]]  # 人机交互需要展示的数据
    ui_type: Optional[str]  # 操作返回的ui类型

    # 决策路由
    intent: Optional[str]

    # 文件数据
    file_name: Optional[str]
    file_path: Optional[str]
    file_content: Optional[bytes]

    # rag数据
    rag_query_params: Optional[dict]
    rag_query_results: Optional[list[str]]


# 定义路由的目标选项
class RouteDecision(BaseModel):
    """根据用户的意图选择下一个执行的节点"""
    destination: Literal["academic", "info", "admin", "chat"] = Field(
        description="下一步的执行节点。academic=教务/成绩/课表, info=讲座/新闻/校规/保研政策, admin=请假/申请, chat=其他闲聊"
    )
