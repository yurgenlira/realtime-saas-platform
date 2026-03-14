from fastapi import FastAPI

app = FastAPI(title="Realtime SaaS Platform")


@app.get("/health")
def health():
    return {"status": "ok"}
