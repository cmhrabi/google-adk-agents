# Current Memory Setup - What Works and What Doesn't

## What You Have Now

Your agent is configured with:
- ✅ Session persistence via SQLite (`my_agent/sessions.db`)
- ✅ Memory callback that saves sessions after each interaction
- ⚠️ In-memory memory storage (InMemoryMemoryService)

## What This Means

### Within a Single Conversation (Same Server Session)

✅ **Works:**
- Ask multiple questions: "What time is it in Tokyo?", "What time is it in London?"
- Ask: "How many time requests have I made?"
- The agent can count because it has access to the **current conversation history**
- PreloadMemoryTool can search memories saved **during this server run**

### Across Server Restarts

❌ **Doesn't Work:**
- Restart the server
- Ask: "What did I ask you yesterday?"
- The agent **cannot remember** because InMemoryMemoryService **loses data on restart**

## Why This Happens

Google ADK has **TWO separate storage systems**:

1. **Session Service** (`--session_service_uri`)
   - Stores: Raw conversation history (messages, events)
   - Your setup: SQLite ✅ Persistent
   - Purpose: Continue conversations, restore chat history

2. **Memory Service** (`--memory_service_uri`)
   - Stores: Searchable semantic memories extracted from sessions
   - Your setup: InMemoryMemoryService (default) ❌ Not persistent
   - Purpose: Answer questions about past interactions across sessions

## Current Behavior

### Test Case 1: Single Session Memory ✅

```bash
# Start server
./run_agent.sh

# In browser at http://localhost:8000:
User: What time is it in Tokyo?
Agent: [responds with Tokyo time]

User: What time is it in London?
Agent: [responds with London time]

User: How many time requests have I made?
Agent: You've made 2 time requests - one for Tokyo and one for London.
```

**Status: WORKS** - Agent has access to current conversation history.

### Test Case 2: Cross-Session Memory ❌

```bash
# Start server
./run_agent.sh

# Make some requests, then stop server (Ctrl+C)
# Restart server
./run_agent.sh

# In browser:
User: What did I ask you about earlier today?
Agent: I don't have access to previous sessions.
```

**Status: DOESN'T WORK** - InMemoryMemoryService loses data on restart.

## How to Fix

To enable **persistent memory across restarts**, you need Vertex AI RAG:

1. Set up Google Cloud credentials
2. Create a RAG corpus
3. Run with:
   ```bash
   adk web . \
     --session_service_uri="sqlite:///$(pwd)/my_agent/sessions.db" \
     --memory_service_uri="rag://your-rag-corpus-id"
   ```

See `MEMORY_SETUP.md` for full instructions.

## Debugging

When you run `./run_agent.sh`, look for these debug messages in your terminal:

```
[MEMORY DEBUG] Memory service type: InMemoryMemoryService
[MEMORY DEBUG] Saving session abc-123 to memory (user: default-user)...
[MEMORY DEBUG] Session saved! Total events in session: 4
```

If you see these messages:
- ✅ Callback is working
- ✅ Sessions are being saved to memory
- ⚠️ But it's InMemoryMemoryService, so data is lost on restart

## Bottom Line

**Current setup is good for:**
- Development and testing
- Single conversation memory (within same server session)
- Understanding how the memory system works

**Current setup is NOT good for:**
- Production use
- Remembering things across server restarts
- Long-term memory of user interactions

**To get true persistent memory:** Set up Vertex AI RAG memory service.
