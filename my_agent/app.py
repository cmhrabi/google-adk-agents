"""
Application setup with custom SQLite memory service.
Exports both memory_service and session_service for the CLI to use.
"""
from google.adk.apps.app import App
from google.adk.sessions import InMemorySessionService
from my_agent.agent import _agent
from my_agent.sqlite_memory_service import SqliteMemoryService

# Create services that the CLI will inject into the Runner
memory_service = SqliteMemoryService(db_path="my_agent/memory.db")
session_service = InMemorySessionService()

# Create the app
app = App(
    name="my_agent",
    root_agent=_agent
)

print("[APP] Initialized with SQLite memory service", flush=True)
