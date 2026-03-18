from fastapi import APIRouter, BackgroundTasks, Depends

from ..core.auth import verify_api_key
from ..services.ingestion import push_to_queue

router = APIRouter(prefix="/v1/webhooks")


@router.post("/ingest", status_code=202)
async def ingest(
    payload: dict, background: BackgroundTasks, tenant_id: str = Depends(verify_api_key)
):
    background.add_task(push_to_queue, tenant_id, payload)
    return {"status": "accepted", "tenant": tenant_id}
