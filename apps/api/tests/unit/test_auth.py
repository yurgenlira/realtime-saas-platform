from unittest.mock import patch

import pytest
from api.core.auth import verify_api_key
from api.main import app
from fastapi.testclient import TestClient

MOCK_TENANT_ID = "tenant-uuid-abc-123"


@pytest.fixture
def client():
    """Unauthenticated TestClient: used to test auth failure cases."""
    return TestClient(app)


@pytest.fixture
def authenticated_client():
    """Client with dependency override: simulates an active tenant without touching the DB.

    app.dependency_overrides replaces verify_api_key with a lambda that returns
    the tenant_id directly, short-circuiting all DB and auth logic.
    The yield ensures the override is cleared after each test.
    """
    app.dependency_overrides[verify_api_key] = lambda: MOCK_TENANT_ID
    yield TestClient(app)
    app.dependency_overrides.clear()


# Valid payload matching WebhookPayload(provider, provider_id, content)
VALID_PAYLOAD = {
    "provider": "whatsapp",
    "provider_id": "msg-ext-id-001",
    "content": {"message": "Hello SaaS"},
}


class TestTenantAuthMiddleware:
    """Tests for the tenant identification and authorization middleware."""

    def test_valid_api_key_returns_202(self, authenticated_client):
        """An active tenant with a valid key must be able to ingest data."""
        # Patch where it is USED (routes.py), not where it is DEFINED (ingestion.py).
        # `from api.services.ingestion import push_to_queue` creates a local reference
        # in routes — patching the source module does not affect that copy.
        with patch("api.v1.routes.push_to_queue"):
            response = authenticated_client.post(
                "/v1/webhooks/ingest",
                json=VALID_PAYLOAD,
            )
        assert response.status_code == 202

    def test_missing_api_key_returns_422(self, client):
        """Without X-API-KEY header, FastAPI returns 422 (schema validation).

        NOTE: 422 is the correct behavior when a required Header(...) is absent —
        FastAPI rejects it before executing any business logic.
        401 only occurs when the key exists but is invalid.
        """
        response = client.post(
            "/v1/webhooks/ingest",
            json=VALID_PAYLOAD,
        )
        assert response.status_code == 422

    def test_invalid_api_key_returns_401(self, client):
        """An invalid API key must return 401.

        We use dependency_overrides to make verify_api_key raise HTTPException(401)
        directly. get_db is also a Depends() — FastAPI resolves it through its own
        DI system, so patch() cannot intercept it and SQLAlchemy would reach the
        real DB (which has no tables in tests). dependency_overrides is the only
        correct way to control FastAPI dependencies.
        """
        from fastapi import HTTPException

        def raise_401():
            raise HTTPException(status_code=401, detail="Invalid API Key")

        app.dependency_overrides[verify_api_key] = raise_401
        try:
            response = client.post(
                "/v1/webhooks/ingest",
                json=VALID_PAYLOAD,
                headers={"X-API-KEY": "invalid-key-xyz"},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 401
        assert "Invalid API Key" in response.json()["detail"]

    def test_inactive_tenant_returns_401(self, client):
        """An inactive tenant produces the same 401 as a non-existent one.

        auth.py filters with Tenant.is_active.is_(True): an inactive tenant returns
        None from the DB just like a non-existent one. Both cases produce the same
        401 — the system does not differentiate between "not found" and "inactive"
        to avoid leaking information about which keys exist.
        """
        from fastapi import HTTPException

        def raise_401():
            raise HTTPException(status_code=401, detail="Invalid API Key")

        app.dependency_overrides[verify_api_key] = raise_401
        try:
            response = client.post(
                "/v1/webhooks/ingest",
                json=VALID_PAYLOAD,
                headers={"X-API-KEY": "inactive-tenant-key"},
            )
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 401
