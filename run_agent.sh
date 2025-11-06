#!/bin/bash

# Run the agent with SQLite-based persistent memory storage
# Memory persists across restarts in my_agent/memory.db

echo "Starting agent with persistent SQLite memory..."
echo "Memory DB: my_agent/memory.db"
echo "Access the web UI at: http://localhost:8000"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the agent - it will use the custom SqliteMemoryService from app.py
adk web .
