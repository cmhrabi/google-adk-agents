# Memory Setup

Your agent supports memory with the following capabilities:

- **Session Persistence** (SQLite): ✅ Conversations persist across restarts
- **Memory Storage** (In-Memory): ⚠️ Memories reset when server restarts

## Important Limitation

The current setup uses `InMemoryMemoryService` which stores memories in RAM only. This means:
- ✅ Agent can remember things **within the same conversation**
- ✅ Session history is saved to SQLite and persists
- ❌ Memories are **lost when you restart the server**
- ❌ Agent cannot recall information from previous server sessions

**For persistent memory across restarts**, you need to configure Vertex AI RAG (see Advanced Usage below).

## Quick Start

Run your agent with persistent memory:

```bash
./run_agent.sh
```

This will start a web UI at http://localhost:8000

Or manually:

```bash
adk web . --session_service_uri="sqlite:///$(pwd)/my_agent/sessions.db"
```

## How It Works

1. **Session Persistence**: All conversations are saved to `my_agent/sessions.db`
2. **Memory Callback**: After each interaction, the `auto_save_session_to_memory_callback` saves the session to memory
3. **Memory Retrieval**: The `PreloadMemoryTool()` allows the agent to search and retrieve past conversations

## Testing Persistent Memory

### Test 1: Verify Session Persistence

```bash
# Start the agent
./run_agent.sh

# Open http://localhost:8000 in your browser
# In the same session, ask questions:
> What time is it in Tokyo?
> What time is it in London?

# Note: The agent saves each session to memory via the callback
# Ask the agent to recall:
> What did I ask you about?
```

The agent should remember your previous questions.

### Test 2: Count Requests

```bash
# Start the agent
./run_agent.sh

# Open http://localhost:8000 in your browser
# Make several requests in the conversation:
> What time is it in London?
> What time is it in New York?
> What time is it in Sydney?

# Ask the agent to count
> How many time requests have I made?
```

The agent should be able to count your requests by searching its memory using the PreloadMemoryTool.

## Database Files

- `my_agent/sessions.db` - Stores session data (conversations, state)
- `my_agent/memory.db` - Would store memory data (currently using InMemoryMemoryService via CLI default)

## Important Notes

1. **Same Session Continuity**: By default, the CLI creates a new session each time. To continue the same session, you need to specify the session_id.

2. **Memory vs Sessions**:
   - Sessions store the conversation history
   - Memory stores semantic information extracted from sessions
   - Your callback saves sessions to memory after each interaction

3. **Database Location**: The SQLite databases are stored in the `my_agent/` directory and persist across runs.

## Advanced Usage

### Enable Persistent Memory Across Restarts (Vertex AI RAG)

To have memories persist across server restarts, you need to use Vertex AI RAG:

1. **Set up Google Cloud credentials** in `.env`:
   ```bash
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

2. **Create a RAG corpus** (one-time setup):
   ```bash
   # You'll need to create a RAG corpus in Google Cloud
   # See: https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/rag-api
   ```

3. **Run with both session and memory persistence**:
   ```bash
   adk web . \
     --session_service_uri="sqlite:///$(pwd)/my_agent/sessions.db" \
     --memory_service_uri="rag://your-rag-corpus-id"
   ```

### Specify a different database location

```bash
adk web . --session_service_uri="sqlite:////path/to/your/sessions.db"
```

### Use different port

```bash
adk web . --session_service_uri="sqlite:///$(pwd)/my_agent/sessions.db" --port 8080
```

## Troubleshooting

### Database locked error
If you get a "database is locked" error, make sure you don't have multiple instances of the agent running.

### Agent doesn't remember past conversations
Make sure you're:
1. Using the same session_id across runs (or the agent needs to search memory)
2. Running with the `--session_service_uri` flag
3. The callback is executing (check for errors in console)

### Clear the database
To start fresh:

```bash
rm my_agent/sessions.db my_agent/memory.db
```
