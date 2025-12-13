import os
import json
from databases.crud import get_enabled_tools
from databases.database import SessionLocal
from bedrock.converse import Converse
from langchain.agents import create_agent
from tools.web_search import (
    DuckDuckGo,
    Arxiv,
    Wikipedia,
    GoogleSearch,
    GoogleScholar,
    GoogleTrends,
    AskNews,
    RedditSearch,
    SearxSearch,
    OpenWeather,
)

TOOL_CLASS_MAP = {
    "duckduckgo": DuckDuckGo,
    "arxiv": Arxiv,
    "wikipedia": Wikipedia,
    "google_search": GoogleSearch,
    "google_scholar": GoogleScholar,
    "google_trends": GoogleTrends,
    "asknews": AskNews,
    "reddit": RedditSearch,
    "searx": SearxSearch,
    "openweather": OpenWeather
}
from databases.crud import get_llm_by_name, get_agent_by_name

class PromptFactory:
    def __init__(self):
        pass
    
    def load_agent_prompt() -> str:
        """Load system prompt for the agent."""
        prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/agent-prompt.txt")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"[Agent] Prompt file not found: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
        
    def load_llm_prompt() -> str:
        """Load system prompt for the llm."""
        prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/llm-prompt.txt")
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"[Agent] Prompt file not found: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
        
class AgentFactory:
    """Factory for creating LangChain agents with dynamically enabled tools."""

    def __init__(self):
        self.chat_converse = Converse()
        self.GENERAL_ASSISTANT_PROMPT = PromptFactory.load_agent_prompt()

    async def get_enabled_tools(self):
        """Fetch all enabled tools from the DB and return a list of tool classes."""
        tools = []
        async with SessionLocal() as session:
            db_tools = await get_enabled_tools(session)

            for t in db_tools:
                tool_cls = TOOL_CLASS_MAP.get(t.name)
                if tool_cls:
                    tools.append(tool_cls)

        return tools
    
    async def get_llm(self, model_name: str):
        """Fetch the LLM from the database and return it."""
        async with SessionLocal() as session:
            llm = await get_llm_by_name(session, model_name)
        
        return llm

    async def get_agent(self, agent_name: str):
        """Fetch the agent from the database and return it."""
        async with SessionLocal() as session:
            agent = await get_agent_by_name(session, agent_name)
        
        return agent
    
    async def agent(self, agent_name: str, model_name: str):
        """Create and return an LLM agent with appropriate model and tools."""
        agent_name = (agent_name or "").lower()
        model_name = (model_name or "").lower()
        
        agent = await self.get_agent(agent_name)
        if not agent:
            return None

        llm = await self.get_llm(model_name)
        if not llm:
            return None
        
        agent_llm_ids = json.loads(agent.llm_ids)
        if str(llm.id) not in [str(item['id']) for item in agent_llm_ids]:
            return None
        
        build_converse = self.chat_converse.build_converse(llm)

        system_active_tools = await self.get_enabled_tools()
        
        agent_tools = json.loads(agent.tools)
        agent_active_tools = [TOOL_CLASS_MAP.get(t['name']) for t in agent_tools]

        # Use tool name for intersection due to unhashable StructuredTool
        system_active_tool_names = {tool.name for tool in system_active_tools if tool is not None}
        active_tools = [tool for tool in agent_active_tools if tool and tool.name in system_active_tool_names]

        agent = create_agent(
            system_prompt=agent.system_prompt,
            tools=active_tools,
            model=build_converse,
        ).with_config({"recursion_limit": 200})

        # Create the LangChain agent
        return agent

class LLMFactory:
    def __init__(self):
        self.chat_converse = Converse()
    
    def llm(self, model_name: str):
        """Create and return an LLM model."""
        model_name = (model_name or "").lower()

        if model_name == "claude":
            llm = self.chat_converse.claude_model_text()
        elif model_name == "llama":
            # llm = self.chat_converse.titan_model_text()
            return None
        elif model_name == "gpt-oss":
            # llm = self.chat_converse.mistral_model_text()
            return None
        else:
            raise ValueError(f"[Agent] Unsupported model: {model_name}")
        
        return llm