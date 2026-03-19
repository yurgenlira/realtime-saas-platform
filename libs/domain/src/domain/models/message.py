import uuid

from domain.models.base import Base
from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, func


class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), index=True, nullable=False)
    payload = Column(JSON)
    provider_id = Column(String, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
