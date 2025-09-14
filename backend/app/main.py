from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import health, documents, analysis
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting cramCortex backend...")
    yield
    # Shutdown
    print("Shutting down cramCortex backend...")


app = FastAPI(
    title="cramCortex API",
    description="AI-Powered Test Structure Analyzer",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)