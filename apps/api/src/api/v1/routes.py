from api.core.auth import verify_api_key
from api.services.ingestion import push_to_queue
from api.v1.schemas import WebhookPayload
from fastapi import APIRouter, BackgroundTasks, Depends

router = APIRouter(prefix="/v1/webhooks")


@router.post("/ingest", status_code=202)
async def ingest(
    payload: WebhookPayload,
    background: BackgroundTasks,
    tenant_id: str = Depends(verify_api_key),
):
    background.add_task(push_to_queue, tenant_id, payload.model_dump())
    return {"status": "accepted", "tenant": tenant_id}
