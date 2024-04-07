import asyncio
import json
import logging
import os

import aiohttp
from fastapi import FastAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI()


# Test root endpoint and ollama endpoint
async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://backend:8000") as res:
            if res.status == 200:
                response = await res.json()
                logger.info(response)

        url = "http://ollama:11434/api/generate"
        data = {"model": "open-hermes-2-4_0", "prompt": "Why is the sky blue?"}

        async with session.post(url, data=json.dumps(data)) as res:
            if res.status == 200:
                buffer = ""
                async for chunk in res.content.iter_any():
                    buffer += chunk.decode()
                    if buffer.endswith("\n"):
                        response = json.loads(buffer)
                        logger.info(response.get("response"))
                        buffer = ""


# Check the openapi schema
async def get_schema():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://backend:8000/openapi.json") as res:
            if res.status == 200:
                response = await res.json()
                logger.info(response)

    return response


async def ollama_input(input):
    async with aiohttp.ClientSession() as session:
        url = "http://ollama:11434/api/generate"
        data = {
            "model": "open-hermes-2-4_0",
            "prompt": f"Based on this schema: {input} finish this endpoint for weather. Only output endpoint: http://backend:8000",
        }

        async with session.post(url, data=json.dumps(data)) as res:
            if res.status == 200:
                buffer = ""
                responses = []
                async for chunk in res.content.iter_any():
                    buffer += chunk.decode()
                    if buffer.endswith("\n"):
                        response = json.loads(buffer)
                        responses.append(response)
                        logger.info(response.get("response"))
                        buffer = ""

    return responses


# Get weather data
async def get_weather():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://backend:8000/weathers") as res:
            if res.status == 200:
                response = await res.json()
                logger.info(response)
            else:
                logging.error(f"Failed to get weather data: {res.status}")
                data = await get_schema()
                response = await ollama_input(json.dumps(data))

    return response


if __name__ == "__main__":
    asyncio.run(main())

task = asyncio.create_task(main())
task_2 = asyncio.create_task(get_schema())
task_3 = asyncio.create_task(get_weather())
