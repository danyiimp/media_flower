import aiohttp
from fastapi import HTTPException


async def download_image(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status,
                    detail="Failed to download image",
                )
            return await response.read()
