from langchain_core.messages import SystemMessage, HumanMessage

from backend.app.agents.agentBase import AgentBase
from backend.app.agents.agentPrompts import get_rag_summary_system_prompt, get_rag_query_system_prompt
from backend.app.agents.llmBase import LLMBase
from backend.app.models.graphState import GraphState
from backend.app.models.ragModels import RagQuery
from backend.app.agents.embeddingModelBase import EmbeddingModelBase
from backend.app.db.session import get_qdrant
from qdrant_client.http import models


async def info_graph(state: GraphState):
    print(f"info: {state}")
    return {}


async def rewrite_query_node(state: GraphState):
    messages = state['messages']
    prompt = get_rag_summary_system_prompt(messages[-1].content)
    llm = LLMBase().client
    llm = llm.with_structured_output(RagQuery)
    result = await llm.ainvoke([HumanMessage(content=prompt)])
    return {
        "rag_query_params": result.dict()
    }


async def retrieve_node(state: GraphState):
    # 1. 获取 LLM 生成的参数
    params = state["rag_query_params"]
    hyde_text = params.get("hyde_doc", "")
    keywords = params.get("keywords", "").split(" ")
    domain_val = params.get("domain", "")

    # 2. 初始化模型和客户端
    embedding_model = EmbeddingModelBase().get_model()
    qdrant_client = await get_qdrant()

    # 3. 使用 HyDE 文本生成向量 (语义搜索的核心)
    query_vector = await embedding_model.aembed_query(hyde_text)

    # 4. 执行检索
    search_results = await qdrant_client.query_points(
        collection_name="hfut_policy",
        query=query_vector,
        limit=10,
        with_payload=True,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.domain",
                    match=models.MatchValue(value=domain_val)
                )
            ],
            should=[
                models.FieldCondition(
                    key="content",
                    match=models.MatchText(text=keyword)
                ) for keyword in keywords
            ]
        )
    )

    # 6. 处理结果
    retrieved_texts = [hit.payload["content"] for hit in search_results.points]

    # # 打印调试信息，查看得分
    # for hit in search_results.points:
    #     print(f"DEBUG: Score: {hit.score:.4f} | Content: {hit.payload['content']}")

    if not retrieved_texts:
        print("⚠️ 警告：检索结果为空！请检查 Qdrant 里的 metadata.domain 是否一致。")

    return {
        "rag_query_results": retrieved_texts
    }


async def info_query_node(state: GraphState):
    context_list = state["rag_query_results"]
    system_prompt = get_rag_query_system_prompt(context_list)
    messages = state['messages']
    agent = AgentBase(
        system_prompt=system_prompt
    )
    response = await agent.arun(messages=messages)
    return {
        "messages": [response[-1]]
    }

