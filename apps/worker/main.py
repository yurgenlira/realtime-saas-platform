import json
import os

import redis
from domain.models.message import Message
from domain.models.tenant import Tenant  # noqa: F401
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# # Get URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis configuration
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), decode_responses=True)


def process_event(event_data):
    """
    Persist events in the database.
    """
    # Create a new session for this transaction
    db = SessionLocal()
    try:
        # Map the JSON event to the SQLAlchemy Message model
        new_message = Message(
            tenant_id=event_data.get("tenant_id"),
            payload=event_data.get("payload"),
            # Get provider from payload if exists
            provider_id=event_data.get("payload", {}).get("provider", "system"),
        )

        db.add(new_message)
        db.commit()
        print(f"Saved to DB: Tenant {new_message.tenant_id}")
    except Exception as e:
        print(f"Error saving: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Worker started and listening to 'events_queue'...")
    while True:
        try:
            # brpop is blocking, wait until there is a message
            _, data = r.brpop("events_queue")
            event = json.loads(data)

            print(f"Event received from Tenant: {event['tenant_id']} Processing: {event['payload']}")
            process_event(event)

        except Exception as e:
            print(f"Error in worker main loop: {e}")
