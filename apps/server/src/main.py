from fastapi import FastAPI

from apps.server.src.api.v1.routes import router as webhooks_v1

app = FastAPI(title="Realtime SaaS Platform")

# Register modular routes
app.include_router(webhooks_v1)


@app.get("/health")
def health():
    return {"status": "ok"}
