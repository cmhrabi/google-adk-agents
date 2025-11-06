"""
SQLite-based persistent memory service.
Stores memories in a SQLite database instead of RAM.
"""
import sqlite3
import json
import threading
from google.adk.memory.base_memory_service import BaseMemoryService, SearchMemoryResponse
from google.adk.memory.memory_entry import MemoryEntry
from google.adk.sessions import Session
from google.genai import types
from pathlib import Path


class SqliteMemoryService(BaseMemoryService):
    """A SQLite-based memory service that persists memories across restarts."""

    def __init__(self, db_path: str = "my_agent/memory.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user
                ON memories(app_name, user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_content
                ON memories(content)
            """)
            conn.commit()

    async def add_session_to_memory(self, session: Session):
        """Store session events as searchable memories."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            try:
                for event in session.events:
                    if not event.content or not event.content.parts:
                        continue

                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            # Store each text part as a memory
                            metadata = {
                                'author': event.author,
                                'event_id': event.id if hasattr(event, 'id') else None,
                            }

                            cursor.execute("""
                                INSERT INTO memories (app_name, user_id, session_id, content, metadata)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                session.app_name,
                                session.user_id,
                                session.id,
                                part.text,
                                json.dumps(metadata)
                            ))

                conn.commit()
                print(f"[SQLiteMemoryService] Saved session {session.id} to database", flush=True)
            finally:
                conn.close()

    async def search_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        query: str
    ) -> SearchMemoryResponse:
        """Search memories using keyword matching."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            try:
                # Simple keyword search (case-insensitive)
                search_query = query.lower()

                cursor.execute("""
                    SELECT content, metadata
                    FROM memories
                    WHERE app_name = ?
                    AND user_id = ?
                    AND LOWER(content) LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 10
                """, (
                    app_name,
                    user_id,
                    f'%{search_query}%'
                ))

                results = cursor.fetchall()
                memories = []

                for content_text, metadata_json in results:
                    metadata = json.loads(metadata_json) if metadata_json else {}

                    # Create Content object with the text
                    content = types.Content(
                        parts=[types.Part(text=content_text)],
                        role=metadata.get('author', 'user')
                    )

                    memories.append(MemoryEntry(
                        content=content,
                        author=metadata.get('author')
                    ))

                print(f"[SQLiteMemoryService] Found {len(memories)} memories for query: {search_query}", flush=True)
                return SearchMemoryResponse(memories=memories)

            finally:
                conn.close()

    def clear_all_memories(self):
        """Clear all memories from the database (for testing)."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories")
            conn.commit()
            conn.close()
            print("[SQLiteMemoryService] Cleared all memories", flush=True)
