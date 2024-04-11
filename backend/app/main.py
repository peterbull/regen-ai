from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


# allowed_origins = os.getenv("ALLOWED_ORIGINS").split(",")
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["allowed_origins"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Health check root endpoint of the application.

    Returns:
        dict: A dictionary with a greeting message.
    """
    return {"Hello": "Claudio", "Hi There": "Rosie"}


@app.get("/weather")
async def weather():
    """
    Retrieves all the available weather forecasts.

    Returns:
        dict: A dictionary containing weather information.
            - location (str): The location of the lost and found.
            - temperature (float): The temperature in Fahrenheit.
            - precipitation (float): The precipitation in inches.
    """
    return [
        {"location": "San Diego", "temperature": 72.1, "precipitation": 0},
        {"location": "New York", "temperature": 60.5, "precipitation": 0.2},
        {"location": "Chicago", "temperature": 55.3, "precipitation": 0.1},
        # {"location": "Seattle", "temperature": 65.2, "precipitation": 0.8},
        # {"location": "Miami", "temperature": 80.6, "precipitation": 0.0},
    ]


@app.get("/air_quality")
async def air_quality():
    """
    Retrieves the air quality information

    Returns:
        dict: A dictionary containing the location, AQI (Air Quality Index), and pollutant information.
    """
    return [
        {"location": "San Diego", "AQI": 45, "pollutant": "PM2.5"},
        {"location": "New York", "AQI": 30, "pollutant": "PM10"},
        {"location": "Chicago", "AQI": 55, "pollutant": "PM2.5"},
        # {"location": "Seattle", "AQI": 35, "pollutant": "PM10"},
        # {"location": "Miami", "AQI": 40, "pollutant": "PM2.5"},
    ]


@app.get("/traffic")
async def traffic():
    """
    Get traffic information.

    Returns:
        dict: A dictionary containing traffic information including location, congestion, and average speed.
    """
    return [
        {"location": "San Diego", "congestion": "Moderate", "average_speed": 45.2},
        {"location": "New York", "congestion": "High", "average_speed": 30.5},
        {"location": "Chicago", "congestion": "Low", "average_speed": 55.3},
        # {"location": "Seattle", "congestion": "Moderate", "average_speed": 35.2},
        # {"location": "Miami", "congestion": "High", "average_speed": 40.6},
    ]
