import React from "react";


{
//    This Cis WeatherWidget Component , Used in App.js
}
const WeatherWidget = () => {
  return (
    <div className="row  WeatherWidget  ">
      <div className="container WeatherWidget " id="WeatherWidget">
        <a
          className="weatherwidget-io"
          href="https://forecast7.com/en/53d35n6d26/dublin/"
          data-label_1="DUBLIN"
          data-label_2="WEATHER"
          data-mode="Current"
          data-days="3"
        >
          DUBLIN WEATHER
        </a>
      </div>
    </div>
  );
};

export default WeatherWidget;
