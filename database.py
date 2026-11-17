
import sqlite3

# SQLite database file
DB_NAME = "cloudops.db"


def create_database():
    """Create the monitoring table if it does not exist."""

    with sqlite3.connect(DB_NAME) as conn:
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
