from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from backend.app.graph.graph import get_graph
from backend.app.models.frontModels import FrontUserQuery, FrontUserQueryInterrupt

router = APIRouter()


@router.post("/chat")
async def userQuery(user_query: FrontUserQuery):
    print(user_query)
    query_text = user_query.chat_text
    user_info = {
        'uid': 1,
        'role': 'student',
        'name': '李逍遥',
    }
    graph = get_graph()
    config = {"configurable": {"thread_id": f"{user_info['uid']}-{user_info['role']}"}}
    response = await graph.ainvoke(
        {
            "messages": [HumanMessage(query_text)],
            "user_info": user_info,
            "file_content": user_query.file
        },
        config=config
    )

    return response


@router.post("/chat/interrupt")
async def userQueryInterrupt(user_query: FrontUserQueryInterrupt):
    user_info = {
        'uid': 1,
        'role': 'student',
        'name': '李逍遥',
    }
    graph = get_graph()
    config = {"configurable": {"thread_id": f"{user_info['uid']}-{user_info['role']}"}}
    response = await graph.ainvoke(
        Command(resume=user_query.resume_data),
        config=config
    )
    return response
