from typing import Any

from pydantic import BaseModel


class WebhookPayload(BaseModel):
    provider: str  # "whatsapp" | "telegram"
    provider_id: str  # external message ID
    content: dict[str, Any]
