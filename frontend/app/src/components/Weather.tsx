import { useEffect, useState } from "react";
import AWS from "aws-sdk";
import LocationForecast from "./LocationForecast";

AWS.config.update({
  accessKeyId: process.env.REACT_APP_AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.REACT_APP_AWS_SECRET_ACCESS_KEY,
  region: process.env.REACT_APP_AWS_REGION,
});

const s3 = new AWS.S3();

const Weather: React.FC<any> = () => {
  const [weather, setWeather] = useState<any>([]);
  const [weatherEndpoint, setWeatherEndpoint] = useState<string>(
    "http://localhost:8000/weather"
  );
  const [lastUpdated, setLastUpdated] = useState<Date>(
    new Date("1900-01-01T12:00:00")
  );
  const [fetchCount, setFetchCount] = useState<number>(0);

  const checkAndUpdateEndpoint = async () => {
    if (fetchCount >= 100) return;
    try {
      const params: any = {
        Bucket: process.env.REACT_APP_S3_BUCKET_NAME,
        Key: "endpoints.json",
      };

      const { LastModified }: any = await s3.headObject(params).promise();
      const lastModified = new Date(LastModified);

      if (lastModified > lastUpdated) {
        const { Body }: any = await s3.getObject(params).promise();
        const endpoint = JSON.parse(Body.toString());
        endpoint.weather = endpoint.weather.replace("backend", "localhost");

        setLastUpdated(lastModified);
        setWeatherEndpoint(endpoint.weather);
      }
      setFetchCount((prevCount) => prevCount + 1);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    checkAndUpdateEndpoint();
  }, []);

  useEffect(() => {
    let intervalId: any;

    const fetchWeather = async () => {
      try {
        const res = await fetch(weatherEndpoint);
        if (res.status === 200) {
          const newWeather = await res.json();
          setWeather(newWeather);
        } else if (res.status === 404) {
          setWeather({ error: "Endpoint not found. Checking for updates..." });
          await checkAndUpdateEndpoint();
        } else {
          setWeather({ error: "Failed to fetch weather data." });
        }
      } catch (err) {
        console.error(err);
      }
    };

    if (weatherEndpoint) {
      fetchWeather();
      intervalId = setInterval(fetchWeather, 10000);
    }

    return () => intervalId && clearInterval(intervalId);
  }, [weatherEndpoint]);

  return (
    <div className="font-mono bg-custom-blue p-4 rounded-xl shadow-2xl text-custom-off-white max-w-xl mx-auto mt-8">
      <p className="text-2xl py-2">
        Current Endpoint: {weatherEndpoint.replace("http://localhost:8000", "")}
      </p>
      <div className="grid grid-cols-3 gap-8 px-12">
        {weather.length > 1 ? (
          weather.map((locationForecast: any, index: any) => (
            <div key={index} className="col-span-1">
              <LocationForecast locationForecast={locationForecast} />
            </div>
          ))
        ) : (
          <p className="col-start-2 animate-pulse text-4xl text-custom-mint">
            Healing API
            <br />
            <span className="text-6xl"> ✚ </span>
          </p>
        )}
      </div>
    </div>
  );
};

export default Weather;
