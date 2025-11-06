import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime


DB_PATH = "/Users/calumhrabi/google-adk/my_agent/sessions.db"


def get_past_sessions(
    user_id: str = "user",
    limit: int = 10,
    app_name: str = "my_agent"
) -> List[Dict[str, Any]]:
    """
    Retrieves information about past sessions for a user.

    Args:
        user_id (str): The user ID to query sessions for. Defaults to "user".
        limit (int): Maximum number of sessions to return. Defaults to 10.
        app_name (str): The application name. Defaults to "my_agent".

    Returns:
        List[Dict]: A list of session dictionaries containing:
            - session_id: The unique session identifier
            - create_time: When the session was created
            - update_time: When the session was last updated
            - event_count: Number of events in the session
            - first_message: The first user message in the session
            - last_message: The last user message in the session

    Raises:
        sqlite3.Error: If there's a database error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get sessions with event counts
        query = """
        SELECT
            s.id as session_id,
            s.create_time,
            s.update_time,
            COUNT(e.id) as event_count
        FROM sessions s
        LEFT JOIN events e ON s.id = e.session_id AND s.user_id = e.user_id AND s.app_name = e.app_name
        WHERE s.user_id = ? AND s.app_name = ?
        GROUP BY s.id, s.create_time, s.update_time
        ORDER BY s.update_time DESC
        LIMIT ?
        """

        cursor.execute(query, (user_id, app_name, limit))
        sessions = cursor.fetchall()

        result = []
        for session in sessions:
            session_dict = dict(session)

            # Get first and last user messages for this session
            cursor.execute("""
                SELECT content, timestamp
                FROM events
                WHERE session_id = ? AND user_id = ? AND app_name = ? AND author = 'user'
                ORDER BY timestamp ASC
                LIMIT 1
            """, (session_dict['session_id'], user_id, app_name))

            first_msg = cursor.fetchone()
            if first_msg:
                try:
                    content = json.loads(first_msg['content'])
                    if 'parts' in content and len(content['parts']) > 0:
                        session_dict['first_message'] = content['parts'][0].get('text', '')
                except (json.JSONDecodeError, KeyError):
                    session_dict['first_message'] = None
            else:
                session_dict['first_message'] = None

            cursor.execute("""
                SELECT content, timestamp
                FROM events
                WHERE session_id = ? AND user_id = ? AND app_name = ? AND author = 'user'
                ORDER BY timestamp DESC
                LIMIT 1
            """, (session_dict['session_id'], user_id, app_name))

            last_msg = cursor.fetchone()
            if last_msg:
                try:
                    content = json.loads(last_msg['content'])
                    if 'parts' in content and len(content['parts']) > 0:
                        session_dict['last_message'] = content['parts'][0].get('text', '')
                except (json.JSONDecodeError, KeyError):
                    session_dict['last_message'] = None
            else:
                session_dict['last_message'] = None

            result.append(session_dict)

        conn.close()
        return result

    except sqlite3.Error as e:
        raise sqlite3.Error(f"Database error: {e}")


def get_session_conversation(
    session_id: str,
    user_id: str = "user",
    app_name: str = "my_agent"
) -> Dict[str, Any]:
    """
    Retrieves the full conversation history for a specific session.

    Args:
        session_id (str): The session ID to retrieve conversation for.
        user_id (str): The user ID. Defaults to "user".
        app_name (str): The application name. Defaults to "my_agent".

    Returns:
        Dict: A dictionary containing:
            - session_id: The session identifier
            - create_time: When the session was created
            - update_time: When the session was last updated
            - events: List of events in chronological order, each containing:
                - author: Who generated the event (user or agent)
                - content: The message content
                - timestamp: When the event occurred
                - actions: Any function calls or responses

    Raises:
        sqlite3.Error: If there's a database error
        ValueError: If the session is not found
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get session info
        cursor.execute("""
            SELECT id, create_time, update_time
            FROM sessions
            WHERE id = ? AND user_id = ? AND app_name = ?
        """, (session_id, user_id, app_name))

        session = cursor.fetchone()
        if not session:
            raise ValueError(f"Session {session_id} not found for user {user_id}")

        session_dict = dict(session)
        session_dict['session_id'] = session_dict.pop('id')

        # Get all events for this session
        cursor.execute("""
            SELECT id, author, content, actions, timestamp
            FROM events
            WHERE session_id = ? AND user_id = ? AND app_name = ?
            ORDER BY timestamp ASC
        """, (session_id, user_id, app_name))

        events = cursor.fetchall()
        session_dict['events'] = []

        for event in events:
            event_dict = {
                'event_id': event['id'],
                'author': event['author'],
                'timestamp': event['timestamp']
            }

            # Parse content
            if event['content']:
                try:
                    content = json.loads(event['content'])
                    if 'parts' in content:
                        # Extract text or function calls from parts
                        parts = content['parts']
                        if parts:
                            if 'text' in parts[0]:
                                event_dict['text'] = parts[0]['text']
                            elif 'function_call' in parts[0]:
                                event_dict['function_call'] = parts[0]['function_call']
                            elif 'function_response' in parts[0]:
                                event_dict['function_response'] = parts[0]['function_response']
                except (json.JSONDecodeError, KeyError):
                    event_dict['content'] = event['content']

            # Parse actions if present
            if event['actions']:
                try:
                    event_dict['actions'] = json.loads(event['actions'])
                except (json.JSONDecodeError, TypeError):
                    pass

            session_dict['events'].append(event_dict)

        conn.close()
        return session_dict

    except sqlite3.Error as e:
        raise sqlite3.Error(f"Database error: {e}")


def search_sessions_by_content(
    search_term: str,
    user_id: str = "user",
    app_name: str = "my_agent",
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Searches for sessions containing specific content in user messages.

    Args:
        search_term (str): The term to search for in message content.
        user_id (str): The user ID. Defaults to "user".
        app_name (str): The application name. Defaults to "my_agent".
        limit (int): Maximum number of sessions to return. Defaults to 5.

    Returns:
        List[Dict]: A list of matching sessions with:
            - session_id: The session identifier
            - create_time: When the session was created
            - matching_message: The message that matched the search
            - timestamp: When the matching message was sent

    Raises:
        sqlite3.Error: If there's a database error
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Search for content in user events
        query = """
        SELECT DISTINCT
            e.session_id,
            s.create_time,
            e.content,
            e.timestamp
        FROM events e
        JOIN sessions s ON e.session_id = s.id AND e.user_id = s.user_id AND e.app_name = s.app_name
        WHERE e.author = 'user'
            AND e.user_id = ?
            AND e.app_name = ?
            AND e.content LIKE ?
        ORDER BY e.timestamp DESC
        LIMIT ?
        """

        cursor.execute(query, (user_id, app_name, f'%{search_term}%', limit))
        results = cursor.fetchall()

        sessions = []
        for row in results:
            session_dict = {
                'session_id': row['session_id'],
                'create_time': row['create_time'],
                'timestamp': row['timestamp']
            }

            # Parse the matching message
            try:
                content = json.loads(row['content'])
                if 'parts' in content and len(content['parts']) > 0:
                    session_dict['matching_message'] = content['parts'][0].get('text', '')
            except (json.JSONDecodeError, KeyError):
                session_dict['matching_message'] = None

            sessions.append(session_dict)

        conn.close()
        return sessions

    except sqlite3.Error as e:
        raise sqlite3.Error(f"Database error: {e}")
