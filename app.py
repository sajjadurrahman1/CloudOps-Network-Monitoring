
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

DB_NAME = "cloudops.db"


@app.route("/")
def home():
    return jsonify({
        "application": "CloudOps",
        "message": "Network Monitoring API",
        "status": "running"
    })


@app.route("/api/monitoring")
def get_monitoring_data():

    # Connect to the existing monitoring database
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        records = conn.execute("""
            SELECT id, server, status,
                   response_time, http_status, timestamp
            FROM monitoring
            ORDER BY id DESC
            LIMIT 100
        """).fetchall()

    # Convert database records into JSON
    results = [dict(record) for record in records]

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
