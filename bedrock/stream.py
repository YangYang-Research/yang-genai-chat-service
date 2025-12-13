import asyncio
import traceback
from helpers.loog import logger
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from bedrock.factory import AgentFactory, LLMFactory, PromptFactory
from typing import AsyncGenerator

class Streaming():
    def __init__(self):
        self.agent_factory = AgentFactory()
        self.llm_factory = LLMFactory()
        
    async def agent_astreaming(self, chat_id: str, message: dict, agent_name: str, model_name: str, stream_mode: str) -> AsyncGenerator[str, None]:
        try:
            agent = await self.agent_factory.agent(agent_name=agent_name, model_name=model_name)
            if agent:
                # The ReAct agent returns a dict with 'output'
                async for token, metadata in agent.astream(input=message, stream_mode=stream_mode):
                    if metadata.get("langgraph_node") == "model":
                        content_blocks = token.content_blocks or []
                        for block in content_blocks:
                            if block.get("type") == "text":
                                text = block.get("text", "")
                                if text.strip():
                                    yield text
                                    await asyncio.sleep(0)
                yield "\n"
            else:
                yield f"Agent {agent_name} with model {model_name} not found."
        except Exception as e:
            yield f"\n[Error] {str(e)}"
            logger.error(f"An error occurred: {e} \n TRACEBACK: ", traceback.format_exc())
    
    async def llm_astreaming(self, chat_id: str, message: dict, model_name: str) -> AsyncGenerator[str, None]:
        try:
            llm = self.llm_factory.llm(model_name=model_name)
            if llm:
                    LLM_PROMPT = PromptFactory.load_llm_prompt()
                    lc_messages = [SystemMessage(content=LLM_PROMPT)]

                    for msg in message.get("messages", []):
                        role = msg["role"]
                        text_parts = [part.get("text", "") for part in msg.get("content", []) if part.get("type") == "text"]
                        text = "\n".join(text_parts)

                        if role == "user":
                            lc_messages.append(HumanMessage(content=text))
                        elif role == "assistant":
                            lc_messages.append(AIMessage(content=text))
                        elif role == "system":
                            lc_messages.append(SystemMessage(content=text))

                    async for chunk in llm.astream(input=lc_messages):
                        yield chunk.text
                        await asyncio.sleep(0)
                                        
                    yield "\n"
            else:
                yield f"Model {model_name} not found."
        except Exception as e:
            yield f"\n[Error] {str(e)}"
            logger.error(f"An error occurred: {e} \n TRACEBACK: ", traceback.format_exc())
    
    