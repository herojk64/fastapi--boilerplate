from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.routes.config import REGISTERED_ROUTERS
from app.bootstrap.setup import SETUPS
from app.bootstrap.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

for setup in SETUPS:
    setup(app)

for router in REGISTERED_ROUTERS:
    app.include_router(router, prefix="/api/v1")


@app.get("/api/health")
async def health_check():
    """Health check endpoint for Docker and load balancers."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "fastapi-boilerplate"}
    )

