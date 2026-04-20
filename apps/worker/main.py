import json
import os

import boto3
from domain.models.message import Message
from domain.models.tenant import Tenant  # noqa: F401
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# boto3 client for SQS
sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))
QUEUE_URL = os.getenv("SQS_QUEUE_URL")


# process message from SQS
def process_message(body: dict) -> None:
    """
    Process a message from SQS and save it to the database.
    """
    # Create a new DB session for this transaction
    db = SessionLocal()
    try:
        # Map the JSON event to the SQLAlchemy Message model
        new_message = Message(
            tenant_id=body.get("tenant_id"),
            payload=body.get("payload"),
            # provider_id is extracted from the payload, defaulting to "system" if not present
            provider_id=body.get("payload", {}).get("provider", "system"),
        )
        # Add the new message to the database session
        db.add(new_message)
        # Commit the transaction
        db.commit()
        print(f"Saved to DB: Tenant {new_message.tenant_id}")
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"DB insert failed: {e}") from e
    finally:
        db.close()


if __name__ == "__main__":
    print("Worker started. Long-polling SQS...")
    while True:
        try:
            # Receive messages from SQS
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,
                MessageAttributeNames=["All"],
            )
            for msg in response.get("Messages", []):
                receipt = msg["ReceiptHandle"]
                try:
                    body = json.loads(msg["Body"])
                    print(f"Processing tenant: {body.get('tenant_id')}")
                    process_message(body)
                    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt)
                except Exception as e:
                    print(f"Message processing failed, leaving in queue for retry: {e}")
        except Exception as e:
            print(f"SQS polling error: {e}")
