from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.exceptions import unhandled_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("AI Incident Intelligence API starting...")
    yield
    print("AI Incident Intelligence API shutting down...")


app = FastAPI(
    title="AI Incident Intelligence",
    description="AI-powered incident detection, analysis, and intelligence platform.",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/health")
async def api_health_check():
    return {
        "status": "healthy",
        "api_version": "v1",
    }