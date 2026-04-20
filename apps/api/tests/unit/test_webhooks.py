from unittest.mock import patch

import pytest
from api.core.auth import verify_api_key
from api.main import app
from fastapi.testclient import TestClient

MOCK_TENANT_ID = "tenant-uuid-abc-123"

# Canonical payload matching WebhookPayload(provider, provider_id, content)
VALID_PAYLOAD = {
    "provider": "whatsapp",
    "provider_id": "msg-ext-id-001",
    "content": {"from": "+1234567890", "message": "Hello SaaS"},
}


@pytest.fixture
def authenticated_client():
    """Reusable fixture: full auth bypass, focused on ingestion logic.

    dependency_overrides[verify_api_key] makes FastAPI skip the entire
    authentication chain and return MOCK_TENANT_ID directly as tenant_id.
    This isolates endpoint tests from any DB or auth logic.
    """
    app.dependency_overrides[verify_api_key] = lambda: MOCK_TENANT_ID
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestWebhookIngestionEndpoint:
    """Tests focused on the ingestion endpoint logic, with auth fully bypassed."""

    def test_valid_whatsapp_webhook_returns_202(self, authenticated_client):
        """A valid payload must return 202 and invoke push_to_queue synchronously."""
        with patch("api.v1.routes.push_to_queue"):
            response = authenticated_client.post(
                "/v1/webhooks/ingest",
                json=VALID_PAYLOAD,
            )
        assert response.status_code == 202
        assert response.json()["status"] == "accepted"

    def test_push_to_queue_is_called_on_ingest(self, authenticated_client):
        """push_to_queue must be invoked synchronously before the 202 response."""
        with patch("api.v1.routes.push_to_queue") as mock_push:
            authenticated_client.post(
                "/v1/webhooks/ingest",
                json=VALID_PAYLOAD,
            )
        # Verify that push_to_queue was called exactly once (non-blocking)
        mock_push.assert_called_once()

    def test_response_contains_tenant_id(self, authenticated_client):
        """The response body must include the tenant_id from the auth bypass."""
        with patch("api.v1.routes.push_to_queue"):
            response = authenticated_client.post(
                "/v1/webhooks/ingest",
                json=VALID_PAYLOAD,
            )
        assert response.json()["tenant"] == MOCK_TENANT_ID

    def test_invalid_payload_schema_returns_422(self, authenticated_client):
        """An invalid payload must return 422 and not invoke push_to_queue."""
        response = authenticated_client.post(
            "/v1/webhooks/ingest",
            json={"provider": "whatsapp"},
        )
        assert response.status_code == 422

    def test_push_to_queue_receives_correct_tenant_id(self, authenticated_client):
        """Verify that push_to_queue receives the tenant_id from the auth bypass."""
        with patch("api.v1.routes.push_to_queue") as mock_push:
            authenticated_client.post(
                "/v1/webhooks/ingest",
                json={
                    "provider": "telegram",
                    "provider_id": "tg-msg-789",
                    "content": {"chat_id": "789"},
                },
            )
        call_args = mock_push.call_args
        assert call_args is not None
        # Verify that the first argument is the tenant_id
        assert call_args.args[0] == MOCK_TENANT_ID

    def test_push_to_queue_receives_payload_as_dict(self, authenticated_client):
        """The payload must arrive at push_to_queue as a dict (result of model_dump)."""
        with patch("api.v1.routes.push_to_queue") as mock_push:
            authenticated_client.post("/v1/webhooks/ingest", json=VALID_PAYLOAD)

        pushed_payload = mock_push.call_args.args[1]
        assert isinstance(pushed_payload, dict)
        assert pushed_payload["provider"] == "whatsapp"
        assert pushed_payload["provider_id"] == "msg-ext-id-001"
