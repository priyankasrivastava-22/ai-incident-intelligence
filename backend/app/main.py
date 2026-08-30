from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.exceptions import unhandled_exception_handler

app = FastAPI(
    title="AI Incident Intelligence",
    version="0.1.0",
    description="AI-powered incident intelligence and root cause analysis platform",
)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy"}


@app.get("/api/v1/health")
async def api_v1_health_check():
    return {"status": "healthy", "api_version": "v1"}