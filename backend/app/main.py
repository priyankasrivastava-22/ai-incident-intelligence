from fastapi import FastAPI

app = FastAPI(
    title="AI Incident Intelligence",
    version="0.1.0",
    description="AI-powered incident intelligence and root cause analysis platform",
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}