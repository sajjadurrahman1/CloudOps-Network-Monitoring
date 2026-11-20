
import sqlite3
from pathlib import Path

# SQLite database file
DB_NAME = Path(__file__).resolve().parent / "cloudops.db"


def create_database():
    """Create the monitoring and alerts tables."""

    with sqlite3.connect(DB_NAME) as conn:

        # Store individual server checks.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS monitoring (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time REAL,
                http_status INTEGER,
                timestamp TEXT NOT NULL
            )
        """)

        # Store server outage and recovery events.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server TEXT NOT NULL,
                previous_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)


def save_result(server, status, response_time,
                http_status, timestamp):
    """Save a monitoring result to the database."""

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO monitoring
            (server, status, response_time,
             http_status, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            server,
            status,
            response_time,
            http_status,
            timestamp
        ))

    print("Monitoring result saved to database.")


def get_last_status(server):
    """Retrieve the most recent saved status of a server."""

    with sqlite3.connect(DB_NAME) as conn:
        row = conn.execute("""
            SELECT status
            FROM monitoring
            WHERE server = ?
            ORDER BY id DESC
            LIMIT 1
        """, (server,)).fetchone()

    return row[0] if row else None


def save_alert(server, previous_status,
               new_status, alert_type, timestamp):
    """Save a server outage or recovery event."""

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO alerts
            (server, previous_status, new_status,
             alert_type, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            server,
            previous_status,
            new_status,
            alert_type,
            timestamp
        ))

def get_recent_alerts(limit=20):
    """Retrieve the most recent outage and recovery alerts."""

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT id, server, previous_status,
                   new_status, alert_type, timestamp
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]

    print(f"Alert saved: {alert_type} - {server}")
