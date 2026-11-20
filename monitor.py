
import argparse
import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone

import requests

from database import (
    create_database,
    save_result,
    get_last_status,
    save_alert
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

CONFIG_FILE = Path(__file__).resolve().parent / "servers.json"

MONITOR_INTERVAL = int(
    os.environ.get("MONITOR_INTERVAL", "30")
)

if MONITOR_INTERVAL < 1:
    raise ValueError(
        "MONITOR_INTERVAL must be at least 1 second"
    )


# --------------------------------------------------
# Load and validate servers
# --------------------------------------------------

def load_servers():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        config = json.load(file)

    servers = config["servers"]

    if not isinstance(servers, list) or not servers:
        raise ValueError(
            "'servers' must be a non-empty list"
        )

    for server in servers:
        if (
            not isinstance(server, dict)
            or not isinstance(server.get("name"), str)
            or not isinstance(server.get("url"), str)
            or not server["name"].strip()
            or not server["url"].startswith(("http://", "https://"))
        ):
            raise ValueError(
                "Invalid server configuration"
            )

    return servers


try:
    SERVERS = load_servers()

except (
    FileNotFoundError,
    json.JSONDecodeError,
    KeyError,
    ValueError
) as error:
    raise SystemExit(
        f"CloudOps configuration error: {error}"
    )


# --------------------------------------------------
# Monitor an individual server
# --------------------------------------------------

def check_server(server):
    name = server["name"]
    url = server["url"]

    timestamp = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    try:
        start_time = time.perf_counter()

        response = requests.get(
            url,
            timeout=5
        )

        response_time = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        http_status = response.status_code

        if 200 <= http_status < 400:
            status = "ONLINE"
        else:
            status = "OFFLINE"

    except requests.RequestException as error:
        status = "OFFLINE"
        response_time = None
        http_status = None

        print(f"Request error for {name}: {error}")

    # Display monitoring results
    print(f"Server: {name}")
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Response Time: {response_time}")
    print(f"HTTP Status: {http_status}")
    print(f"Timestamp: {timestamp}")

    # Get the previous status before saving
    previous_status = get_last_status(name)

    # Save current monitoring result
    save_result(
        name,
        status,
        response_time,
        http_status,
        timestamp
    )

    # Generate an alert when status changes
    if previous_status is not None and previous_status != status:

        if previous_status == "ONLINE" and status == "OFFLINE":
            alert_type = "OUTAGE"
            print(
                f"[ALERT] {name} changed "
                "from ONLINE to OFFLINE"
            )

        elif previous_status == "OFFLINE" and status == "ONLINE":
            alert_type = "RECOVERY"
            print(
                f"[RECOVERY] {name} changed "
                "from OFFLINE to ONLINE"
            )

        else:
            alert_type = None

        if alert_type is not None:
            save_alert(
                name,
                previous_status,
                status,
                alert_type,
                timestamp
            )

    print("-" * 40)


# --------------------------------------------------
# Run one monitoring cycle
# --------------------------------------------------

def run_monitoring_cycle():
    for server in SERVERS:
        check_server(server)

    print("Monitoring cycle completed.\n")


# --------------------------------------------------
# Main application
# --------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CloudOps Network Monitoring"
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one monitoring cycle and exit"
    )

    args = parser.parse_args()

    # Initialize SQLite or PostgreSQL
    create_database()

    print("CloudOps Multi-Server Monitoring Started")
    print(f"Monitoring {len(SERVERS)} servers")

    # GitHub Actions mode: run once and exit
    if args.once:
        run_monitoring_cycle()
        print("Single monitoring cycle completed.")
        return

    # Local mode: monitor continuously
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            run_monitoring_cycle()
            time.sleep(MONITOR_INTERVAL)

    except KeyboardInterrupt:
        print("\nCloudOps monitoring stopped.")


if __name__ == "__main__":
    main()
