
import os
import sqlite3
from contextlib import closing

from flask import Flask, jsonify, render_template

from database import (
    create_database,
    get_recent_alerts,
    get_recent_monitoring
)


# Initialize Flask application.
app = Flask(__name__)

# Ensure database tables exist.
create_database()


@app.route("/")
def home():
    """Return the application health status."""

    return jsonify({
        "application": "CloudOps",
        "message": "Network Monitoring API",
        "status": "running"
    })


@app.route("/dashboard")
def dashboard():
    """Render the monitoring dashboard."""

    return render_template("index.html")


@app.route("/api/monitoring")
def get_monitoring_data():
    """Return the latest 100 monitoring records."""

    return jsonify(get_recent_monitoring(limit=100))

    with closing(sqlite3.connect(DB_NAME)) as conn:
        conn.row_factory = sqlite3.Row

        records = conn.execute("""
            SELECT id, server, status,
                   response_time, http_status, timestamp
            FROM monitoring
            ORDER BY id DESC
            LIMIT 100
        """).fetchall()

    results = [dict(record) for record in records]

    return jsonify(results)


@app.route("/api/alerts")
def get_alerts():
    """Return the latest outage and recovery alerts."""

    alerts = get_recent_alerts(limit=20)

    return jsonify(alerts)


if __name__ == "__main__":
    # Hosting platforms usually supply a PORT variable.
    port = int(os.environ.get("PORT", 5001))

    # Keep debug mode disabled unless explicitly enabled.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    # Bind to all interfaces when running the development server.
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
