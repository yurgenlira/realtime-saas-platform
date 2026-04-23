from main import process_batch


def test_full_ingest_flow(api_client, sqs_client, sqs_queue, db_session):
    response = api_client.post(
        "/v1/webhooks/ingest",
        headers={"x-api-key": "integration-key"},
        json={"provider": "whatsapp", "provider_id": "msg_001", "content": {"text": "ping"}},
    )
    assert response.status_code == 202

    queued = sqs_client.receive_message(
        QueueUrl=sqs_queue, MaxNumberOfMessages=1, WaitTimeSeconds=0, VisibilityTimeout=0
    )
    assert len(queued.get("Messages", [])) == 1

    processed = process_batch(sqs_client, sqs_queue, db_session)
    assert processed == 1

    empty = sqs_client.receive_message(QueueUrl=sqs_queue, MaxNumberOfMessages=1, WaitTimeSeconds=0)
    assert len(empty.get("Messages", [])) == 0

    from domain.models.message import Message

    messages = db_session.query(Message).all()
    assert len(messages) == 1
    assert messages[0].tenant_id is not None
