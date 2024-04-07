import asyncio
import json
import logging
import os

import aiohttp
import dspy
from fastapi import FastAPI

logger = logging.getLogger("dspy")

#####################################
# Temporarily overwrite dspy logger #
#####################################
# Remove all handlers from the logger
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create a console handler with a specific log level
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Create a formatter and add it to the handler
formatter = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Fastapi
app = FastAPI()

# DSPy model
llm = dspy.OllamaLocal(
    "open-hermes-2-4_0", base_url="http://ollama:11434", max_tokens=3000, model_type="chat"
)
dspy.settings.configure(lm=llm)


class GenerateEndpoint(dspy.Signature):
    """
    Return the correct endpoint based on the given schema.
    """

    task = dspy.InputField(desc="The error message for the requested endpoint.")
    url = dspy.InputField(desc="The attempted url.")
    context = dspy.InputField(desc="OpenAPI spec for the API.")
    endpoint = dspy.OutputField(desc="The corrected endpoint.")


class EndpointGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.process_endpoint = dspy.ChainOfThought(GenerateEndpoint)

    def forward(self, task, context, url):
        result = self.process_endpoint(task=task, context=context, url=url)
        return result.endpoint


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
        url = "http://backend:8000/weathers"
        async with session.get(url) as res:
            if res.status == 200:
                response = await res.json()
                logger.info(response)
            else:
                logging.error(f"Failed to get weather data: {res.status}")
                content = await res.content.read()
                task = content.decode()
                context = await get_schema()
                # response = await ollama_input(json.dumps(data))
                endpoint_generator = EndpointGenerator()
                endpoint = await asyncio.to_thread(
                    endpoint_generator, task=task, context=json.dumps(context), url=url
                )
                print("hello")
                logger.info(f"Endpoint: {endpoint}")

    return response


if __name__ == "__main__":
    asyncio.run(main())

task = asyncio.create_task(main())
task_2 = asyncio.create_task(get_schema())
task_3 = asyncio.create_task(get_weather())
