import os
from tools import time
from google.adk.agents.llm_agent import Agent, BaseAgent
from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from my_agent import models

root_agent = Agent(
    model=models.open_router_sonnet,
    name='root_agent',
    description="You are a time getting agent for different timezones.",
    instruction="""You are a helpful assistant that gets the time at a specific location using the get_current_time tool.

        You have access to the full conversation history in this session. When asked about previous requests or interactions:
        1. Look at the conversation history to see what the user has asked
        2. Count the number of requests or messages they've sent
        3. Recall specific questions or topics discussed

        You can also use the PreloadMemoryTool to search memories from previous sessions if needed.""",
    tools=[time.get_current_time, PreloadMemoryTool()],
)