from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Clients, check_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.clients = Clients()  # startup
    yield
    await app.state.clients.close()  # shutdown


app = FastAPI(title="Veritas Neuro API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/deps")
async def health_deps():
    results = await check_all(app.state.clients)
    healthy = all(v == "ok" for v in results.values())
    return {"status": "ok" if healthy else "degraded", "dependencies": results}
