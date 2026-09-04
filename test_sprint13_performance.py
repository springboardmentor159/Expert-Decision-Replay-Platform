"""Basic latency and concurrency checks for Sprint 13.

Usage: set BASE_URL, TEST_EMAIL, TEST_PASSWORD, then run this script.
"""
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
EMAIL = os.getenv("TEST_EMAIL")
PASSWORD = os.getenv("TEST_PASSWORD")
REQUESTS_PER_ENDPOINT = int(os.getenv("REQUESTS_PER_ENDPOINT", "10"))

if not EMAIL or not PASSWORD:
    raise SystemExit("Set TEST_EMAIL and TEST_PASSWORD; credentials are never stored in this file.")

login = requests.post(f"{BASE_URL}/auth/login", json={"email": EMAIL, "password": PASSWORD}, timeout=10)
login.raise_for_status()
headers = {"Authorization": f"Bearer {login.json()['access_token']}"}


def measure(path):
    started = time.perf_counter()
    response = requests.get(f"{BASE_URL}{path}", headers=headers, timeout=15)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.raise_for_status()
    return elapsed_ms


for path in ("/decisions?page=1&page_size=20", "/decisions/search?q=decision", "/dashboard/employee", "/reports/decisions?page=1&page_size=20"):
    with ThreadPoolExecutor(max_workers=REQUESTS_PER_ENDPOINT) as executor:
        timings = list(executor.map(lambda _: measure(path), range(REQUESTS_PER_ENDPOINT)))
    ordered = sorted(timings)
    p95 = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    print(f"{path}: min={min(timings):.1f}ms mean={statistics.mean(timings):.1f}ms p95={p95:.1f}ms max={max(timings):.1f}ms")

print("Concurrent read checks: PASS")
