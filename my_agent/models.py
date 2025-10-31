import os
from google.adk.models.lite_llm import LiteLlm


#Good for most tasks
open_router_sonnet = LiteLlm(
        api_base=os.getenv("OPENROUTER_BASE_URL"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model='openrouter/anthropic/claude-sonnet-4.5',
    )

#Good for small tasks like routing
open_router_haiku = LiteLlm(
    api_base=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="openrouter/anthropic/claude-4.5-haiku"
)