import sqlite3
import json
import os

DB_PATH = "tickets.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT,
            text TEXT,
            intent TEXT,
            status TEXT,
            resolution TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_ticket(ticket):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets (ticket_id, text, intent, status, resolution)
        VALUES (?, ?, ?, ?, ?)
    """, (
        ticket["ticket_id"],
        ticket["text"],
        ticket["intent"],
        ticket["status"],
        json.dumps(ticket["resolution"])
    ))

    conn.commit()
    conn.close()


def list_tickets(limit=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket_id, text, intent, status, resolution
        FROM tickets ORDER BY id DESC LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "ticket_id": row[0],
            "text": row[1],
            "intent": row[2],
            "status": row[3],
            "resolution": json.loads(row[4])
        }
        for row in rows
    ]


# ✅ ADD THIS FUNCTION (THIS IS WHAT YOUR SERVER NEEDS)
def ticket_exists(ticket_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM tickets WHERE ticket_id = ?", (ticket_id,))
    exists = cursor.fetchone() is not None

    conn.close()
    return exists

def count_tickets():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tickets")
    total = cur.fetchone()[0]
    conn.close()
    return total

