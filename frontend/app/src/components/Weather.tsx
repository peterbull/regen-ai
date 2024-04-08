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
        s3.headObject(params, function (err, data: any) {
          if (err) console.log(err, err.stack); // an error occurred
          else {
            const lastModified = new Date(data.LastModified);
            if (lastModified > lastUpdated) {
              setLastUpdated(lastModified);
              s3.getObject(params, function (err, data: any) {
                if (err) console.log(err, err.stack);
                else {
                  let endpoint = JSON.parse(data.Body.toString());
                  endpoint.weather = endpoint.weather.replace(
                    "backend",
                    "localhost"
                  );
                  setWeatherEndpoint(endpoint.weather);
                  console.log(endpoint.weather);
                }
              });
            }
          }
        });
      } catch (error) {
        console.error(error);
      }
    };
    fetchEndpoint();
    const intervalId = setInterval(fetchEndpoint, 10000);
    return () => clearInterval(intervalId); // Clear interval on component unmount
  }, [lastUpdated]);

  useEffect(() => {
    const fetchWeather = async () => {
      const res = await fetch(weatherEndpoint);
      const data = await res.json();
      setWeather(data);
      console.log(data);
    };
    fetchWeather();
  }, [weatherEndpoint]);

  return (
    <>
      <p>{JSON.stringify(weather)}</p>
    </>
  );
};

export default Weather;
