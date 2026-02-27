import datetime
import json

from langchain_core.messages import ToolMessage

from ..models.graphState import GraphState
from ..agents.agentBase import AgentBase
from ..tools.campusTools import create_campus_tools
from ..agents.agentPrompts import get_academic_agent_prompt


async def academic_graph(state: GraphState):
    print(f"academic: {state}")
    return {}


async def academic_query_node(state: GraphState):
    messages = state['messages']
    user_info = state['user_info']
    agent = AgentBase(
        system_prompt=get_academic_agent_prompt(user_info=user_info, current_time=str(datetime.datetime.now())),
        tools=create_campus_tools(),
    )
    response = await agent.arun(messages=messages)
    # 1. 提取结构化数据
    structured_data = []
    # 从后往前找第一个 ToolMessage
    for msg in reversed(response):
        if isinstance(msg, ToolMessage):
            try:
                # 尝试解析 JSON 字符串
                content = msg.content
                if isinstance(content, str):
                    structured_data = json.loads(content)
                else:
                    structured_data = content
            except Exception as e:
                print(f"数据解析失败: {e}")
                structured_data = []
            break
    return {
        "messages": [response[-1]],
        "structured_data": structured_data
    }
