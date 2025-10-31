import os
from tools import time
from google.adk.agents.llm_agent import Agent

from my_agent import models

#Do not rename agent or file as they are keywords for google ADK
root_agent = Agent(
    model=models.open_router_sonnet,
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[time.get_current_time],
)
