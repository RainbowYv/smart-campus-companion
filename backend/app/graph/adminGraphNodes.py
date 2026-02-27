from datetime import datetime

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import interrupt, Command

from backend.app.agents.agentBase import AgentBase
from backend.app.agents.agentPrompts import get_rag_summary_system_prompt, get_rag_query_system_prompt, \
    get_leave_system_prompt
from backend.app.agents.llmBase import LLMBase
from backend.app.models.frontModels import LeaveData
from backend.app.models.graphState import GraphState

from backend.app.agents.embeddingModelBase import EmbeddingModelBase
from backend.app.db.session import get_qdrant, get_async_db
from qdrant_client.http import models

from backend.app.models.tableModels import LeaveRequest, LeaveStatus


async def admin_graph(state: GraphState):
    print(f"info: {state}")
    return {}


async def admin_leave_node(state: GraphState):
    messages = state['messages']
    system_prompt = get_leave_system_prompt(state["user_info"], datetime.now().strftime("%Y-%m-%d"))
    llm = LLMBase().client
    llm = llm.with_structured_output(LeaveData)
    extracted = await llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=messages)])

    missing_fields = []
    if not extracted.leave_type:
        missing_fields.append("请假类型(事假/病假)")
    if not extracted.start_date:
        missing_fields.append("开始日期")
    if not extracted.end_date:
        missing_fields.append("结束日期")
    if not extracted.reason:
        missing_fields.append("请假原因")

    if missing_fields:
        response = f"好的，为了帮您办理请假，还需要请您提供：{', '.join(missing_fields)}。"
        return {
            "messages": [AIMessage(content=response)]
        }
    response = "已为您生成请假条草稿，请确认无误后提交。"
    user_response = interrupt({
        "ui_type": "",
        "interrupt_data": extracted.dict(),
        "messages": [AIMessage(content=response)]
    })

    print(f"leave: user_response: {user_response}")
    if user_response.get("action") == "cancel":
        return {"messages": [AIMessage(content="您已取消请假申请。")]}

    # 6. 使用 Command 路由到下一步（数据库写入节点）
    return Command(
        goto="save_leave_db_node",
        update={
            "interrupt_data": user_response.get("data"),
            "messages": [AIMessage(content="正在为您提交请假申请...")]
        }
    )


async def save_leave_db_node(state: GraphState):
    data = state["interrupt_data"]
    user_id = state["user_info"]["uid"]

    async with get_async_db() as db:
        # 将字符串转为 Date 对象
        s_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        e_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

        # 写入数据库
        new_leave = LeaveRequest(
            student_id=user_id,
            leave_type=data["leave_type"],
            start_date=s_date,
            end_date=e_date,
            reason=data["reason"],
            status=LeaveStatus.PENDING  # 状态为待审批
        )
        db.add(new_leave)
        await db.commit()

    return {
        "messages": [AIMessage(content="✅ 您的请假申请已成功提交，请等待辅导员审批。")],
        "interrupt_data": None  # 释放状态
    }
