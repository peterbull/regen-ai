const LocationForecast: React.FC<any> = ({ locationForecast }) => {
  const { temperature, precipitation, location } = locationForecast;

  return (
    <div className="flex flex-col items-center p-4">
      {/* Displaying temperature in a larger font size */}
      <p className="text-4xl font-bold text-custom-off-white">{temperature}°</p>

      {/* Precipitation info, displayed in a smaller font size below the temperature */}
      <p className="text-lg text-custom-off-white mt-2">{precipitation}</p>

      {/* Location info, even smaller and below precipitation */}
      <p className="text-base text-custom-off-white mt-1">{location}</p>
    </div>
  );
};
export default LocationForecast;
