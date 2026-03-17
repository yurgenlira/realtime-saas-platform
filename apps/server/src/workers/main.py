import json
import os
import time

import redis

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), decode_responses=True)

if __name__ == "__main__":
    print("Worker listening for events...")
    while True:
        _, data = r.brpop("events_queue")
        event = json.loads(data)
        print(f"[Tenant: {event['tenant_id']}] Processing: {event['payload']}")
        time.sleep(1)  # load simulation
