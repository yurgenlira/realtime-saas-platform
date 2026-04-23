import os
import sys
import uuid
from pathlib import Path

import boto3
import pytest

# apps/worker/main.py is a script, not an installed package — add apps/worker/ to path
# so `from main import process_batch` resolves directly to apps/worker/main.py
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "apps" / "worker"))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SQS_WAIT_TIME_SECONDS", "0")

LOCALSTACK_ENDPOINT = "http://localhost:4566"
AWS_TEST_REGION = "us-east-1"

os.environ["AWS_ENDPOINT_URL"] = LOCALSTACK_ENDPOINT
os.environ["AWS_DEFAULT_REGION"] = AWS_TEST_REGION
os.environ["AWS_ACCESS_KEY_ID"] = "test"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test"


@pytest.fixture(scope="session")
def sqs_client():
    return boto3.client(
        "sqs",
        region_name=AWS_TEST_REGION,
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )


@pytest.fixture
def sqs_queue(sqs_client):
    queue_name = f"test-queue-{uuid.uuid4().hex[:8]}"
    response = sqs_client.create_queue(QueueName=queue_name)
    queue_url = response["QueueUrl"]
    os.environ["SQS_QUEUE_URL"] = queue_url
    yield queue_url
    sqs_client.delete_queue(QueueUrl=queue_url)


@pytest.fixture
def db_session():
    from domain.models.base import Base
    from domain.models.message import Message  # noqa: F401 — registers Message with Base.metadata

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        yield session


@pytest.fixture
def api_client(sqs_queue):
    from api.main import app
    from domain.database import get_db
    from domain.models.base import Base
    from domain.models.tenant import Tenant
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        with TestSession() as s:
            yield s

    with TestSession() as s:
        s.add(Tenant(name="Integration Tenant", api_key="integration-key", is_active=True))
        s.commit()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
