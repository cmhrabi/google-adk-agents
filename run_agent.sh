#!/bin/bash

# Run the agent with SQLite-based persistent memory and session storage
# Memory persists across restarts in my_agent/memory.db
# Sessions persist across restarts in my_agent/sessions.db

echo "Starting agent with persistent SQLite storage..."
echo "Session DB: my_agent/sessions.db"
echo "Access the web UI at: http://localhost:8000"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run with SQLite sessions and memory plugin
# The plugin will inject our custom SqliteMemoryService
adk web . \
  --session_service_uri="sqlite:///$(pwd)/my_agent/sessions.db"
