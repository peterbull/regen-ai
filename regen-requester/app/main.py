import asyncio
import json
import logging
import os

import aiohttp
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)

app = FastAPI()


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://backend:8000") as res:
            if res.status == 200:
                response = await res.json()
                logging.info(response)

        url = "http://ollama:11434/api/generate"
        data = {"model": "open-hermes-2-4_0", "prompt": "Why is the sky blue?"}

        async with session.post(url, data=json.dumps(data)) as res:
            if res.status == 200:
                buffer = ""
                async for chunk in res.content.iter_any():
                    buffer += chunk.decode()
                    if buffer.endswith("\n"):
                        response = json.loads(buffer)
                        logging.info(response)
                        buffer = ""


task = asyncio.create_task(main())
