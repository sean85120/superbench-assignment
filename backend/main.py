import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.src.apis import agent_router, chat_router, health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    logger.info("Starting up application...")

    # Export OpenAPI schema to file on startup
    logger.info("Exporting OpenAPI schema...")
    openapi_schema = app.openapi()

    # Save to project root
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)

    logger.info(f"OpenAPI schema exported to {os.path.abspath('openapi.json')}")

    yield

    # Shutdown events
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(title="AI Agent Service", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(agent_router)


if __name__ == "__main__":
    import asyncio
    import os

    import uvicorn

    from backend.scripts.init_db import create_tables

    # Check if database file exists
    db_path = "ai_agent.db"
    if not os.path.exists(db_path):
        logger.info("Database file not found. Creating tables...")
        asyncio.run(create_tables())
        logger.info("Database tables created successfully.")
    else:
        logger.info("Database file already exists.")

    uvicorn.run(app, host="0.0.0.0", port=8000)
