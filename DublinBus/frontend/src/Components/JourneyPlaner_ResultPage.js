import React, { Component } from "react";
import AppViewHeader from "./AppViewHeader";
import AppViewFavourAndLogin from "./AppViewFavourAndLogin";
import ResultPageButton from "./SlideShowMobileMap";
import "../Static/StyleSheet/ResultPageDestination.css";
import DataProvider from "./DataProvider";
import JourneyPlannerResultsDisplay from "./JourneyPlannerResultsDisplay";

{
  //This Component is the Result page of Search By Destination
}
class JourneyPlaner_ResultPage extends Component {
  render() {
    const color = ["#F65314", "#7CBB00", "#00A1F1", "#FFBB00", "#146EB4"];
    var attractions = this.props.match.params.PickedTouristAttraction.split(
      ","
    );

    return (
      <div
        className="EntireBox  container col-md-12  position-absolute bg-light"
        id="EntireBox_ResultDestination"
      >
        <div className="container ">
          <AppViewHeader SearchState={"Real time Information"} />
          <AppViewFavourAndLogin />
        </div>
        <DataProvider
          endpoint="touristplanner"
          updateMap={this.props.updateMap}
          attractions={JSON.stringify(attractions)}
          startLat={this.props.match.params.startLat}
          startLon={this.props.match.params.startLon}
          home={this.props.match.params.home}
          backend={this.props.backend}
          render={data => (
            <JourneyPlannerResultsDisplay
              updateMap={this.props.updateMap}
              backend={this.props.backend}
              data={data}
            />
          )}
        />

        <ResultPageButton markers={this.props.markers} polyline={this.props.polyline} />

      </div>
    );
  }
}

export default JourneyPlaner_ResultPage;
