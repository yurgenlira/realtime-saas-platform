import json
import os

import boto3

_sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))
_queue_url = os.getenv("SQS_QUEUE_URL")


def push_to_queue(tenant_id: str, payload: dict) -> None:
    _sqs.send_message(
        QueueUrl=_queue_url,
        MessageBody=json.dumps({"tenant_id": tenant_id, "payload": payload}),
        MessageAttributes={
            "tenant_id": {
                "StringValue": tenant_id,
                "DataType": "String",
            }
        },
    )
