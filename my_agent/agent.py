import os
from tools import time
from google.adk.agents.llm_agent import Agent, BaseAgent
from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from my_agent import models

async def auto_save_session_to_memory_callback(callback_context):
    import sys
    # Check if memory_service is available before using it
    memory_service = callback_context._invocation_context.memory_service
    print(f"[MEMORY DEBUG] Memory service type: {type(memory_service).__name__}", file=sys.stderr, flush=True)

    if memory_service is not None:
        session = callback_context._invocation_context.session
        print(f"[MEMORY DEBUG] Saving session {session.id} to memory (user: {session.user_id})...", file=sys.stderr, flush=True)
        await memory_service.add_session_to_memory(session)
        print(f"[MEMORY DEBUG] Session saved! Total events in session: {len(session.events)}", file=sys.stderr, flush=True)
    else:
        print("[MEMORY DEBUG] No memory_service available in context", file=sys.stderr, flush=True)

#Do not rename agent or file as they are keywords for google ADK
_agent = Agent(
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
    after_agent_callback=auto_save_session_to_memory_callback
)

# For CLI compatibility - export as root_agent
root_agent = _agent
