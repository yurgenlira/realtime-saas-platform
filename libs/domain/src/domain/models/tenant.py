import uuid

from domain.models.base import Base
from sqlalchemy import JSON, Boolean, Column, String


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    db_config = Column(JSON, nullable=True)
