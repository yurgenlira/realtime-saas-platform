from api.core.database import get_db
from domain.models.tenant import Tenant
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session


async def verify_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    tenant = (
        db.query(Tenant).filter(Tenant.api_key == x_api_key, Tenant.is_active.is_(True)).first()
    )
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return str(tenant.id)
