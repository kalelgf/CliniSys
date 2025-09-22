from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="CliniSys", openapi_url="/uc-admin/openapi.json", docs_url="/uc-admin/docs")

@app.get("/")
async def root():
    return {"message": "CliniSys Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
