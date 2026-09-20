"""
Main entry point for user management system.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from user_management.users.presentation.api_router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
	yield


app = FastAPI(title="MindPal User Management API", version="1.0.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1/users")


@app.get("/health")
async def health_check():
	return {"status": "healthy"}
