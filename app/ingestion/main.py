"""
Main entry point for ingestion system.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from ingestion.presentation.api_router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
	yield


app = FastAPI(title="MindPal Ingestion API", version="1.0.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1/ingestion")


@app.get("/health")
async def health_check():
	return {"status": "healthy"}
