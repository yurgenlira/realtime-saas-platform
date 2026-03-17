import json
import os

import redis

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), decode_responses=True)


def push_to_queue(tenant_id, payload):
    event = {"tenant_id": tenant_id, "payload": payload}
    r.lpush("events_queue", json.dumps(event))
