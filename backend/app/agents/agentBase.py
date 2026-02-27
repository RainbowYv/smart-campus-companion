from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langchain_core.tools import Tool, BaseTool
from langchain.agents import create_agent

from .llmBase import LLMBase
from ..core.config import get_settings


class AgentBase:
    def __init__(
            self,
            name: Optional[str] = None,
            llm: Optional[BaseChatModel] = None,
            system_prompt: Optional[str] = None,
            tools: Optional[list[BaseTool]] = None,
    ):
        settings = get_settings()
        self.name = name
        self.llm = llm or LLMBase()
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.agent = self.__create_agent()

    def __create_agent(self):
        return create_agent(
            model=self.llm.client,
            system_prompt=self.system_prompt,
            tools=self.tools
        )

    async def arun(
            self,
            messages: list[AnyMessage]
    ) -> AnyMessage:
        response = await self.agent.ainvoke({
            "messages": messages
        })
        return response["messages"][-2:]
