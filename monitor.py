
import json
from pathlib import Path
import requests
import time
from datetime import datetime

from database import create_database, save_result


# Load monitoring targets from servers.json.
CONFIG_FILE = Path(__file__).resolve().parent / "servers.json"


def load_servers():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        config = json.load(file)

    servers = config["servers"]

    # Ensure at least one server is configured.
    if not isinstance(servers, list) or not servers:
        raise ValueError(
            "'servers' must be a non-empty list"
        )

    # Validate each server configuration.
    for server in servers:
        if (
            not isinstance(server, dict)
            or not isinstance(server.get("name"), str)
            or not isinstance(server.get("url"), str)
            or not server["name"].strip()
            or not server["url"].startswith(("http://", "https://"))
        ):
            raise ValueError("Invalid server configuration")

    return servers


# Handle configuration errors gracefully.
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


def check_server(server):
    name = server["name"]
    url = server["url"]

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    try:
        start_time = time.perf_counter()

        response = requests.get(url, timeout=5)

        response_time = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        http_status = response.status_code

        if 200 <= http_status < 400:
            status = "ONLINE"
        else:
            status = "OFFLINE"

    except requests.RequestException:
        status = "OFFLINE"
        response_time = None
        http_status = None

    # Display monitoring results.
    print(f"Server: {name}")
    print(f"URL: {url}")
    print(f"Status: {status}")
    print(f"Response Time: {response_time}")
    print(f"HTTP Status: {http_status}")
    print(f"Timestamp: {timestamp}")

    # Save one monitoring record to the database.
    save_result(
        name,
        status,
        response_time,
        http_status,
        timestamp
    )

    print("-" * 40)


def main():
    create_database()

    print("CloudOps Multi-Server Monitoring Started")
    print(f"Monitoring {len(SERVERS)} servers")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            for server in SERVERS:
                check_server(server)

            print("Monitoring cycle completed.\n")
            time.sleep(30)

    except KeyboardInterrupt:
        print("\nCloudOps monitoring stopped.")


if __name__ == "__main__":
    main()
