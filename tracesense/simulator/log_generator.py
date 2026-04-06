import requests
import random
import time
from datetime import datetime, timezone
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Created some fake deployment logs for MVP purpose .

NORMAL_TEMPLATES = {
    "payment-service": [
        "POST /charge user_id={uid} amount={amt} status=200 duration={dur}ms",
        "Charge successful stripe_id=ch_{sid}",
        "Payment processed for order_{oid}",
    ],
    "order-service": [
        "POST /create-order user_id={uid} status=200 duration={dur}ms",
        "Order created successfully order_id={oid}",
        "Inventory verified for order_{oid}",
    ],
    "inventory-service": [
        "Stock check OK item_id={iid} quantity={qty}",
        "GET /check-stock status=200 duration={dur}ms",
    ],
    "postgres-db": [
        "query OK table=orders duration={dur}ms connections={conn}/100",
        "query OK table=inventory duration={dur}ms connections={conn}/100",
    ],
    "frontend-service": [
        "POST /checkout user_id={uid} status=200 duration={dur}ms",
        "Checkout complete for user_{uid}",
    ]
}

INCIDENT_TEMPLATES = [
    {
        "service": "postgres-db",
        "level":   "WARN",
        "message": "query slow table=inventory duration={dur}ms connections={conn}/100",
        "delay":   0
    },
    {
        "service": "postgres-db",
        "level":   "WARN",
        "message": "connection pool pressure connections={conn}/100 queries queuing",
        "delay":   1
    },
    {
        "service": "postgres-db",
        "level":   "ERROR",
        "message": "query timeout table=inventory duration=5001ms connection pool FULL",
        "delay":   2
    },
    {
        "service": "inventory-service",
        "level":   "ERROR",
        "message": "upstream timeout host=postgres-db duration=3002ms stock check failed",
        "delay":   3
    },
    {
        "service": "order-service",
        "level":   "ERROR",
        "message": "inventory check failed service=inventory-service status=503 order unverifiable",
        "delay":   5
    },
    {
        "service": "payment-service",
        "level":   "WARN",
        "message": "rejected charge order not in verified state order_id={oid}",
        "delay":   6
    },
    {
        "service": "frontend-service",
        "level":   "ERROR",
        "message": "payment failed user_id={uid} code=402 payment rejected checkout failed",
        "delay":   7
    },
]
REDIS_FAILURE_INCIDENT = [
    {
        "service": "cache-service",
        "level":   "WARN",
        "message": "Redis memory usage at 89% — eviction policy active maxmemory-policy allkeys-lru",
        "delay":   0
    },
    {
        "service": "cache-service",
        "level":   "WARN",
        "message": "Redis connection pool exhausted — max clients 500 reached — new connections refused",
        "delay":   2
    },
    {
        "service": "session-service",
        "level":   "ERROR",
        "message": "session lookup failed — Redis unreachable — falling back to database",
        "delay":   3
    },
    {
        "service": "cache-service",
        "level":   "ERROR",
        "message": "Redis READONLY error — replica promoted but master unavailable — writes failing",
        "delay":   4
    },
    {
        "service": "order-service",
        "level":   "ERROR",
        "message": "cart data lost — Redis evicted session keys — user cart empty on checkout",
        "delay":   6
    },
    {
        "service": "payment-service",
        "level":   "ERROR",
        "message": "duplicate payment detected — idempotency key missing from cache — transaction unsafe",
        "delay":   7
    },
    {
        "service": "frontend-service",
        "level":   "ERROR",
        "message": "checkout failed — cart unexpectedly empty — user_id={uid} session lost",
        "delay":   8
    },
]

K8S_CRASHLOOP_INCIDENT = [
    {
        "service": "kubernetes",
        "level":   "WARN",
        "message": "pod payment-service-7x9k2 restarted 3 times in last 5 minutes — CrashLoopBackOff approaching",
        "delay":   0
    },
    {
        "service": "payment-service",
        "level":   "ERROR",
        "message": "OOMKilled — container exceeded memory limit 512Mi — process terminated by kernel",
        "delay":   1
    },
    {
        "service": "kubernetes",
        "level":   "ERROR",
        "message": "pod payment-service-7x9k2 CrashLoopBackOff — back-off 5m0s restarting failed container",
        "delay":   2
    },
    {
        "service": "api-gateway",
        "level":   "ERROR",
        "message": "upstream payment-service no healthy pods available — all instances down",
        "delay":   4
    },
    {
        "service": "order-service",
        "level":   "ERROR",
        "message": "payment processing unavailable — payment-service endpoint returning 503 — orders halted",
        "delay":   5
    },
    {
        "service": "notification-service",
        "level":   "WARN",
        "message": "order confirmation emails queuing — payment events not received — queue depth 847",
        "delay":   6
    },
    {
        "service": "frontend-service",
        "level":   "ERROR",
        "message": "payment gateway unavailable — user_id={uid} checkout blocked — service degraded",
        "delay":   7
    },
]

def simulate_k8s_crashloop():
    print("\n--- INCIDENT: Kubernetes CrashLoopBackOff ---\n")
    base_time = time.time()
    for stage in K8S_CRASHLOOP_INCIDENT:
        while time.time() < base_time + stage["delay"]:
            time.sleep(0.1)
        vals = random_vals()
        message = stage["message"].format(**vals)
        send_log(stage["service"], stage["level"], message)
    print("\n--- K8s crashloop incident complete ---\n")

NETWORK_PARTITION_INCIDENT = [
    {
        "service": "load-balancer",
        "level":   "WARN",
        "message": "health check failing for us-east-1b — 3 consecutive failures — removing from pool",
        "delay":   0
    },
    {
        "service": "postgres-db",
        "level":   "ERROR",
        "message": "replication lag critical — replica us-east-1b 47 seconds behind primary — split brain risk",
        "delay":   1
    },
    {
        "service": "load-balancer",
        "level":   "ERROR",
        "message": "us-east-1b completely removed from pool — all traffic rerouted to us-east-1a — capacity at 200%",
        "delay":   2
    },
    {
        "service": "postgres-db",
        "level":   "ERROR",
        "message": "primary overloaded — connection count 1847/1000 — queries queuing — response time 8900ms",
        "delay":   4
    },
    {
        "service": "order-service",
        "level":   "ERROR",
        "message": "database write timeout after 9000ms — order_{oid} not persisted — data loss risk",
        "delay":   6
    },
    {
        "service": "inventory-service",
        "level":   "ERROR",
        "message": "stock count inconsistent — reads from stale replica — overselling risk detected",
        "delay":   7
    },
    {
        "service": "payment-service",
        "level":   "ERROR",
        "message": "transaction rollback failed — database unreachable — payment state unknown order_id={oid}",
        "delay":   8
    },
    {
        "service": "frontend-service",
        "level":   "ERROR",
        "message": "checkout error — payment state unknown — user_id={uid} shown generic error",
        "delay":   9
    },
]

def simulate_network_partition():
    print("\n--- INCIDENT: Network Partition Split Brain ---\n")
    base_time = time.time()
    for stage in NETWORK_PARTITION_INCIDENT:
        while time.time() < base_time + stage["delay"]:
            time.sleep(0.1)
        vals = random_vals()
        message = stage["message"].format(**vals)
        send_log(stage["service"], stage["level"], message)
    print("\n--- Network partition incident complete ---\n")


def simulate_redis_failure():
    print("\n--- INCIDENT: Redis Cache Failure ---\n")
    base_time = time.time()
    for stage in REDIS_FAILURE_INCIDENT:
        while time.time() < base_time + stage["delay"]:
            time.sleep(0.1)
        vals = random_vals()
        message = stage["message"].format(**vals)
        send_log(stage["service"], stage["level"], message)
    print("\n--- Redis incident complete ---\n")

def random_vals():
    return {
        "uid":  random.randint(10000, 99999),
        "amt":  round(random.uniform(9.99, 299.99), 2),
        "dur":  random.randint(120, 180),
        "oid":  f"{random.randint(1000,9999)}x{random.randint(10,99)}",
        "sid":  random.randint(100000, 999999),
        "iid":  random.randint(1, 500),
        "qty":  random.randint(1, 100),
        "conn": random.randint(10, 40),
    }


def send_log(service, level, message):
    log = {
        "service":   service,
        "level":     level,
        "message":   message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        res = requests.post(f"{BACKEND_URL}/ingest", json=log)
        print(f"[{log['timestamp']}] {level:5} [{service}] {message}")
    except Exception as e:
        print(f"Failed to send log: {e}")


def simulate_normal_traffic(duration_seconds=20):
    print(f"\n--- Normal traffic ({duration_seconds}s) ---\n")
    end = time.time() + duration_seconds
    while time.time() < end:
        service  = random.choice(list(NORMAL_TEMPLATES.keys()))
        template = random.choice(NORMAL_TEMPLATES[service])
        message  = template.format(**random_vals())
        send_log(service, "INFO", message)
        time.sleep(random.uniform(0.2, 0.5))


def simulate_incident():
    print("\n--- INCIDENT: Black Friday DB cascade ---\n")
    base_time = time.time()

    for stage in INCIDENT_TEMPLATES:
        while time.time() < base_time + stage["delay"]:
            time.sleep(0.1)

        vals         = random_vals()
        vals["dur"]  = random.randint(3000, 5500)
        vals["conn"] = random.randint(85, 100)

        message = stage["message"].format(**vals)
        send_log(stage["service"], stage["level"], message)

    print("\n--- Incident complete ---\n")


if __name__ == "__main__":
    print("TraceSense Simulator starting...")

    print("Phase 1: Normal traffic")
    simulate_normal_traffic(duration_seconds=15)

    print("Phase 2: Black Friday DB cascade")
    simulate_incident()
    simulate_normal_traffic(duration_seconds=8)

    print("Phase 3: Memory Leak cascade")
    simulate_memory_leak_incident()
    simulate_normal_traffic(duration_seconds=8)

    print("Phase 4: Redis Cache failure")
    simulate_redis_failure()
    simulate_normal_traffic(duration_seconds=8)

    print("Phase 5: Kubernetes CrashLoopBackOff")
    simulate_k8s_crashloop()
    simulate_normal_traffic(duration_seconds=8)

    print("Phase 6: Network Partition")
    simulate_network_partition()
    simulate_normal_traffic(duration_seconds=8)

    print("\nAll incidents simulated. ChromaDB fully loaded.")