from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.v1.routes import router as webhooks_v1

app = FastAPI(title="Realtime SaaS Platform")

# Register modular routes
app.include_router(webhooks_v1)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Liveness + Readiness probe.

    Verifies:
    - API process is running (liveness)
    - Database connection is reachable (readiness)

    Returns 200 if both pass, 503 if DB is unreachable.
    Used by ALB health checks (Sprint 4) and monitoring (Sprint 6).
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "database": "unreachable", "error": str(e)},
        )
