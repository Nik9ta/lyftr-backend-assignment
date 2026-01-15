import sqlite3
from datetime import datetime
from app.config import settings
from app.schemas import MessagePayload


def insert_message(payload: MessagePayload):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO messages (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.message_id,
                payload.from_,
                payload.to,
                payload.ts,
                payload.text,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
        return "created"

    except sqlite3.IntegrityError:
        return "duplicate"

    finally:
        conn.close()


def get_messages(limit, offset, from_, since, q):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        WHERE 1=1
    """
    params = []

    if from_:
        query += " AND from_msisdn = ?"
        params.append(from_)

    if since:
        query += " AND ts >= ?"
        params.append(since)

    if q:
        query += " AND text LIKE ?"
        params.append(f"%{q}%")

    cursor.execute(f"SELECT COUNT(*) FROM ({query})", params)
    total = cursor.fetchone()[0]

    query += " ORDER BY ts ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append(
            {
                "message_id": r[0],
                "from": r[1],
                "to": r[2],
                "ts": r[3],
                "text": r[4],
            }
        )

    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def get_stats():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT from_msisdn, COUNT(*)
        FROM messages
        GROUP BY from_msisdn
        ORDER BY COUNT(*) DESC
        LIMIT 10
        """
    )
    messages_per_sender = [
        {"from": r[0], "count": r[1]} for r in cursor.fetchall()
    ]

    cursor.execute("SELECT MIN(ts), MAX(ts) FROM messages")
    first_ts, last_ts = cursor.fetchone()

    conn.close()

    return {
        "total_messages": total_messages,
        "senders_count": len(messages_per_sender),
        "messages_per_sender": messages_per_sender,
        "first_message_ts": first_ts,
        "last_message_ts": last_ts,
    }
