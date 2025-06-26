import argparse
import asyncio

from loguru import logger

from backend.src.db.database import engine
from backend.src.models.models import Base


async def create_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")


async def drop_tables():
    """Drop all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables dropped successfully.")


async def recreate_tables():
    """Drop all tables and recreate them."""
    await drop_tables()
    await create_tables()
    logger.info("Database tables recreated successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database setup utility")
    parser.add_argument(
        "--action",
        choices=["create", "drop", "recreate"],
        default="create",
        help="Action to perform on the database (default: create)",
    )

    args = parser.parse_args()

    if args.action == "create":
        asyncio.run(create_tables())
    elif args.action == "drop":
        asyncio.run(drop_tables())
    elif args.action == "recreate":
        asyncio.run(recreate_tables())
