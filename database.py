
import sqlite3
from pathlib import Path
from contextlib import closing

# SQLite database file
DB_NAME = Path(__file__).resolve().parent / "cloudops.db"


def create_database():
    """Create monitoring and alerts tables if they do not exist."""

    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:

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

            # Store outage and recovery events.
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
    """Save one monitoring result to SQLite."""

    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
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

    with closing(sqlite3.connect(DB_NAME)) as conn:
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
    """Save an outage or recovery event."""

    with closing(sqlite3.connect(DB_NAME)) as conn:
        with conn:
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

    print(f"Alert saved: {alert_type} - {server}")


def get_recent_alerts(limit=20):
    """Retrieve recent outage and recovery alerts."""

    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT id, server, previous_status,
                   new_status, alert_type, timestamp
            FROM alerts
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]
