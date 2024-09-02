import asyncio
from app.core.db_init import db


async def upgrade():
    await db.images.create_index("deleted")
    await db.images.create_index(["project_name", "image_name", "deleted"])


if __name__ == "__main__":
    asyncio.run(upgrade())
