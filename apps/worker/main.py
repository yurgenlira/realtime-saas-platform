import json
import logging
import os
import time

import boto3
from domain.database import SessionLocal
from domain.models.message import Message
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# fail fast at startup if the env var is missing — avoids silent misconfiguration
SQS_QUEUE_URL = os.environ["SQS_QUEUE_URL"]
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_sqs_client():
    kwargs = {"region_name": AWS_REGION}
    # AWS_ENDPOINT_URL redirects boto3 to LocalStack in tests; absent in production
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    return boto3.client("sqs", **kwargs)


def process_batch(sqs_client, queue_url: str, db: Session) -> int:
    # extracted from main() so tests can call one cycle without a while True loop
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        # SQS_WAIT_TIME_SECONDS=0 in tests to avoid blocking pytest for 20s
        WaitTimeSeconds=int(os.environ.get("SQS_WAIT_TIME_SECONDS", "20")),
        MessageAttributeNames=["All"],
    )
    messages = response.get("Messages", [])
    for msg in messages:
        try:
            attrs = msg.get("MessageAttributes", {})
            tenant_id = attrs["tenant_id"]["StringValue"]
            data = json.loads(msg["Body"])

            db.add(Message(tenant_id=tenant_id, payload=data["payload"]))
            db.commit()  # atomic ACK: delete only after successful DB write

            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg["ReceiptHandle"],
            )
            logger.info("processed message tenant_id=%s", tenant_id)
        except Exception:
            db.rollback()
            # message stays in SQS and reappears after visibility_timeout expires
            logger.exception("failed to process message — will requeue after visibility timeout")
    return len(messages)


def main():
    sqs = get_sqs_client()
    logger.info("worker started, polling queue=%s", SQS_QUEUE_URL)
    while True:
        try:
            with SessionLocal() as db:
                processed = process_batch(sqs, SQS_QUEUE_URL, db)
                if processed == 0:
                    time.sleep(1)  # brief pause when queue is empty to avoid busy-wait
        except Exception:
            logger.exception("unhandled error in worker loop")
            time.sleep(5)  # back-off on infrastructure failure (DB down, SQS unreachable)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
