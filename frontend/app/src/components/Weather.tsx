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
  const [weatherEndpoint, setWeatherEndpoint] = useState<any>(
    "http://localhost:8000/weather"
  );
  const [lastUpdated, setLastUpdated] = useState<Date>(
    new Date("1900-01-01T12:00:00")
  );

  const [fetchCount, setFetchCount] = useState<number>(0);

  useEffect(() => {
    const fetchEndpoint = async () => {
      if (fetchCount >= 100) return;
      try {
        const params: any = {
          Bucket: process.env.REACT_APP_S3_BUCKET_NAME,
          Key: "endpoints.json",
        };

        const { LastModified }: any = await s3.headObject(params).promise();
        const lastModified: Date = new Date(LastModified);

        if (lastModified > lastUpdated) {
          const { Body }: any = await s3.getObject(params).promise();
          const endpoint = JSON.parse(Body.toString());
          endpoint.weather = endpoint.weather.replace("backend", "localhost");

          setLastUpdated(lastModified);
          setWeatherEndpoint(endpoint.weather);
        }
        setFetchCount(fetchCount + 1); // Add this line
      } catch (err) {
        console.error(err);
      }
    };

    fetchEndpoint();
  }, [lastUpdated, weatherEndpoint]);

  useEffect(() => {
    let intervalId: any;

    const fetchWeather = async () => {
      try {
        const res = await fetch(weatherEndpoint);
        if (res.status === 200) {
          const newWeather = await res.json();
          if (JSON.stringify(newWeather) !== JSON.stringify(weather)) {
            setWeather(newWeather);
          }
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
    <div className="bg-custom-blue p-4 rounded shadow text-custom-off-white">
      <p>
        Current Endpoint: {weatherEndpoint.replace("http://localhost:8000", "")}
      </p>
      <div className="grid grid-cols-3 gap-4">
        {weather.length > 1 ? (
          weather.map((locationForecast: any, index: any) => (
            <div key={index} className="col-span-1">
              <LocationForecast locationForecast={locationForecast} />
            </div>
          ))
        ) : (
          <p className="col-start-2">{JSON.stringify(weather)}</p>
        )}
      </div>
    </div>
  );
};

export default Weather;
