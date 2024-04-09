import { useEffect, useState } from "react";
import AWS from "aws-sdk";

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

  useEffect(() => {
    const fetchEndpoint = async () => {
      try {
        const params: any = {
          Bucket: process.env.REACT_APP_S3_BUCKET_NAME,
          Key: "endpoints.json",
        };

        const data: any = await s3.headObject(params).promise();
        const lastModified = new Date(data.LastModified);
        if (lastModified > lastUpdated) {
          setLastUpdated(lastModified);
          const new_data: any = await s3.getObject(params).promise();
          let endpoint = JSON.parse(new_data.Body.toString());
          endpoint.weather = endpoint.weather.replace("backend", "localhost");
          setWeatherEndpoint(endpoint.weather);
          console.log(endpoint.weather);
        }
      } catch (err: any) {
        console.log(err, err.stack);
      }
    };
    fetchEndpoint();
  }, [weather, lastUpdated]);

  useEffect(() => {
    const fetchWeather = async () => {
      const res = await fetch(weatherEndpoint);
      if (res.status !== 200) {
        setWeather([{ weather: "Endpoint Changed" }]);
      } else {
        const data = await res.json();
        setWeather(data);
      }
      console.log(weatherEndpoint);
    };
    fetchWeather();

    const intervalId = setInterval(fetchWeather, 10000);
    return () => clearInterval(intervalId); // Clear interval on component unmount
  }, [weatherEndpoint]);

  return (
    <>
      <p>{JSON.stringify(weather)}</p>
    </>
  );
};

export default Weather;
