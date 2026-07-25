"""Prometheus metrics exporter.
Exposes counters and histograms to be scraped by Prometheus.

Run:
  python app/metrics_exporter.py
Browse:
  http://localhost:8000/metrics
"""
import time
import random
from prometheus_client import start_http_server, Counter, Histogram

REQUESTS = Counter("llm_requests_total", "Total LLM requests made")
LATENCY = Histogram("llm_request_latency_seconds", "Latency per LLM request")

def simulate_work():
    start = time.time()
    # Simulate variable latency
    time.sleep(random.uniform(0.1, 1.2))
    LATENCY.observe(time.time() - start)
    REQUESTS.inc()

def main():
    start_http_server(8000)
    print("Serving metrics on :8000 ... Ctrl+C to stop.")
    while True:
        simulate_work()

if __name__ == "__main__":
    main()
