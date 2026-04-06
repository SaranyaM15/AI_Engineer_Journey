import json
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from log_generator import (
    NORMAL_TEMPLATES,
    INCIDENT_TEMPLATES,
    MEMORY_LEAK_INCIDENT,
    REDIS_FAILURE_INCIDENT,
    K8S_CRASHLOOP_INCIDENT,
    NETWORK_PARTITION_INCIDENT,
    random_vals
)

from datetime import datetime, timezone

logs = []

def make_log(service, level, message):
    return {
        "service":   service,
        "level":     level,
        "message":   message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# normal traffic
for _ in range(30):
    service  = random.choice(list(NORMAL_TEMPLATES.keys()))
    template = random.choice(NORMAL_TEMPLATES[service])
    logs.append(make_log(service, "INFO", template.format(**random_vals())))

# all 5 incidents
for incident in [
    INCIDENT_TEMPLATES,
    MEMORY_LEAK_INCIDENT,
    REDIS_FAILURE_INCIDENT,
    K8S_CRASHLOOP_INCIDENT,
    NETWORK_PARTITION_INCIDENT
]:
    for stage in incident:
        vals         = random_vals()
        vals["dur"]  = random.randint(3000, 5500)
        vals["conn"] = random.randint(85, 100)
        message      = stage["message"].format(**vals)
        logs.append(make_log(stage["service"], stage["level"], message))

output_path = os.path.join(
    os.path.dirname(__file__), "..", "backend", "seed_logs.json"
)

with open(output_path, "w") as f:
    json.dump(logs, f, indent=2)

print(f"Generated {len(logs)} seed logs → backend/seed_logs.json")