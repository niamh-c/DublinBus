import React, { Component } from "react";
import { Link } from "react-router-dom";
import "../Static/StyleSheet/HomePage.css";
{
  //This Component is the HomePage of the mobile view port
}
class HomePage extends Component {
  render() {
    return (
      <div
        className="EntireBox HomePage container col-md-12  position-absolute "
        id="EntireBox_HomePage"
      >
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
        <div className="container HomePageContains">
          <div className="container  ">
            <div className="row ">
              <Link to={"/SearchByStop"} className="LinkCss ">
                <button type="button" className="btn btn-success">
                  Search By Stop
                </button>
              </Link>
            </div>

            <div className="row">
              <Link to={"/SearchByDestination"} className="LinkCss">
                <button type="button" className="btn btn-success">
                  Search By Destination
                </button>
              </Link>
            </div>

            <div className="row">
              <Link to={"/JourneyPlanner"} className="LinkCss">
                <button type="button" className="btn btn-success">
                  Tourist Planner
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default HomePage;
