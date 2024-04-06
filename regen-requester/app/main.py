import asyncio
import json
import logging
import os

import aiohttp
from fastapi import FastAPI

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

app = FastAPI()


# Test root endpoint and ollama endpoint
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
                        logging.info(response.get("response"))
                        buffer = ""


# Check the openapi schema
async def get_schema():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://backend:8000/openapi.json") as res:
            if res.status == 200:
                response = await res.json()
                logging.info(response)

    return response


async def get_weather():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://backend:8000/weather") as res:
            if res.status == 200:
                response = await res.json()
                logging.info(response)

    return response


task = asyncio.create_task(main())
task_2 = asyncio.create_task(get_schema())
task_3 = asyncio.create_task(get_weather())
