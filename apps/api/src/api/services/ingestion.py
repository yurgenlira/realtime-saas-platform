import json
import os

import boto3


def push_to_queue(tenant_id: str, payload: dict) -> None:
    sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))
    sqs.send_message(
        QueueUrl=os.environ["SQS_QUEUE_URL"],
        MessageBody=json.dumps({"tenant_id": tenant_id, "payload": payload}),
        MessageAttributes={
            "tenant_id": {
                "StringValue": tenant_id,
                "DataType": "String",
            }
        },
    )
