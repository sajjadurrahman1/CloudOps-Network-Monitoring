
import requests
import time
from datetime import datetime

# Monitor a local test server
SERVER_NAME = "Local Server"
SERVER_URL = "http://127.0.0.1:5000"


def check_server():
    start_time = time.perf_counter()

    try:
        response = requests.get(SERVER_URL, timeout=5)

        response_time = (
            time.perf_counter() - start_time
        ) * 1000

        if 200 <= response.status_code < 400:
            status = "ONLINE"
        else:
            status = "ERROR"

        print("Server:", SERVER_NAME)
        print("Status:", status)
        print("Response Time:", round(response_time, 2), "ms")
        print("HTTP Status:", response.status_code)
        print("Timestamp:", datetime.now())

    except requests.RequestException:
        print("Server:", SERVER_NAME)
        print("Status: OFFLINE")
        print("Response Time: N/A")
        print("HTTP Status: N/A")
        print("Timestamp:", datetime.now())


check_server()
