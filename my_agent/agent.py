import os
from tools import time
from tools.session_history import get_past_sessions, get_session_conversation, search_sessions_by_content
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
    description="You are a time getting agent for different timezones with access to session history.",
    instruction="""You are a helpful assistant that gets the time at a specific location using the get_current_time tool.

        You have access to the full conversation history in this session. When asked about previous requests or interactions:
        1. Look at the conversation history to see what the user has asked in THIS session
        2. Count the number of requests or messages they've sent
        3. Recall specific questions or topics discussed

        You also have access to session history tools to retrieve information from PAST sessions:
        - get_past_sessions: Get a list of recent sessions with summaries
        - get_session_conversation: Get the full conversation for a specific session
        - search_sessions_by_content: Search past sessions for specific content

        Use these tools when users ask about previous sessions, past conversations, or what they've asked before.""",
    tools=[
        time.get_current_time,
        get_past_sessions,
        get_session_conversation,
        search_sessions_by_content
    ],
)