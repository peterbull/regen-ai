import asyncio
import json
import logging
import os
from urllib.parse import urlparse

import aiofiles
import aiohttp
import boto3
import dspy
from botocore.exceptions import ClientError
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
base_url = "http://backend:8000/"


########## Ollama ##########
OLLAMA_MODEL_ALIAS = os.getenv("OLLAMA_MODEL_ALIAS")

# DSPy model
llm = dspy.OllamaLocal(
    f"{OLLAMA_MODEL_ALIAS}", base_url="http://ollama:11434", max_tokens=3000, model_type="chat"
)
dspy.settings.configure(lm=llm)

########## Arize Phoenix ##########
import phoenix as px
from openinference.instrumentation.dspy import DSPyInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

phoenix_session = px.launch_app()
endpoint = "http://phoenix:6006/v1/traces"
resource = Resource(attributes={})
tracer_provider = trace_sdk.TracerProvider(resource=resource)
span_otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter=span_otlp_exporter))

trace_api.set_tracer_provider(tracer_provider=tracer_provider)
DSPyInstrumentor().instrument()


########## Assertions ##########
def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme])
    except ValueError:
        return False


########## DSPy ##########
class GenerateEndpoint(dspy.Signature):
    """
    Return the correct endpoint based on the given schema.
    """

    task = dspy.InputField(desc="The error message for the requested endpoint.")
    url = dspy.InputField(desc="The failed url.")
    base_url = dspy.InputField(desc="The root url for the api.")
    desired_info = dspy.InputField(desc="The desired data to gather from the endpoint.")
    context = dspy.InputField(desc="OpenAPI spec for the API.")
    endpoint = dspy.OutputField(
        desc="The correct endpoint url. IMPORTANT!! This must be just the full new url and nothing else!"
    )


class EndpointGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.process_endpoint = dspy.ChainOfThought(GenerateEndpoint)

    def forward(self, task, context, base_url, url, desired_info):
        result = self.process_endpoint(
            task=task, context=context, base_url=base_url, url=url, desired_info=desired_info
        )
        endpoint = result.endpoint

        # Assertion: Format and syntax validation
        dspy.Suggest(
            is_url(endpoint),
            f"The endpoint '{endpoint}' must be a url that adheres to the API's endpoint format and syntax rules.",
        )

        return endpoint


# class EndpointRefinement(dspy.Module):
#     def __init__(self):
#         super().__init__()
#         self.refine_endpoint = dspy.ChainOfThought(GenerateEndpoint)

#     def forward(self, task, context, base_url, url, desired_info, attempt=1):
#         if attempt > 5:
#             return logger.info("Unable to generate endpoint. Improve process or change models.")

#         result = self.refine_endpoint(
#             task=task, context=context, base_url=base_url, url=url, desired_info=desired_info
#         )
#         endpoint = result.endpoint

#         if not is_url(endpoint):
#             task = f"Please generate a valid endpoint, previous attempt was not a URL: {endpoint}"
#             return self.forward(task, context, base_url, url, desired_info, attempt + 1)

#         return endpoint


########## S3 ##########
S3_AWS_ACCESS_KEY_ID = os.getenv("S3_AWS_ACCESS_KEY_ID")
S3_AWS_SECRET_ACCESS_KEY = os.getenv("S3_AWS_SECRET_ACCESS_KEY")


def upload_to_s3(file_name, bucket, object_name=None):
    s3_client = boto3.client(
        "s3", aws_access_key_id=S3_AWS_ACCESS_KEY_ID, aws_secret_access_key=S3_AWS_SECRET_ACCESS_KEY
    )
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# Test root endpoint and ollama endpoint
async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://backend:8000") as res:
            if res.status == 200:
                response = await res.json()
                logger.info(response)

        url = "http://ollama:11434/api/generate"
        data = {"model": f"{OLLAMA_MODEL_ALIAS}", "prompt": "Why is the sky blue?"}

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
            "model": f"{OLLAMA_MODEL_ALIAS}",
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
        async with aiofiles.open("./app/data/endpoints.json", "r") as f:
            content = await f.read()
            urls = json.loads(content)
        url = urls.get("weather")

        async with session.get(url) as res:
            if res.status == 200:
                response = await res.json()
                logger.info(json.dumps(response, indent=4))
                logger.info(url)
            else:
                logger.error(f"Failed to get weather data: {res.status}")
                content = await res.content.read()
                task = content.decode()
                context = await get_schema()
                endpoint_generator = EndpointGenerator()
                # endpoint_refiner = EndpointRefinement()
                endpoint = await asyncio.to_thread(
                    endpoint_generator,
                    # endpoint_refiner,
                    task=task,
                    context=json.dumps(context),
                    base_url=base_url,
                    desired_info="weather",
                    url=url,
                )
                logger.info(f"Endpoint: {endpoint}")
                async with session.get(endpoint) as new_res:
                    if new_res.status == 200:
                        urls["weather"] = endpoint

                        # Update the endpoints file
                        async with aiofiles.open("./app/data/endpoints.json", "w") as f:
                            await f.write(json.dumps(urls))
                        upload_to_s3(
                            "./app/data/endpoints.json", "regen-requester", "endpoints.json"
                        )
                        return new_res
    return response


async def periodic_weather_update():
    # n = 0
    # while n < 20:
    while True:
        try:
            await get_weather()
        except Exception as e:
            logger.error(f"Failed to update weather: {e}")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())

task = asyncio.create_task(main())
task_2 = asyncio.create_task(get_schema())
task_3 = asyncio.create_task(get_weather())
task_4 = asyncio.create_task(periodic_weather_update())
