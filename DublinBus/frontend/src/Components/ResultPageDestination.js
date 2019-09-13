import React, {Component} from "react";
import AppViewHeader from "./AppViewHeader";
import ResultPageButton from "./SlideShowMobileMap";
import "../Static/StyleSheet/ResultPageDestination.css";
import DataProvider from "./DataProvider";
import Table from "./Table";

{
    //This Component is the Result page of Search By Destination
}
class ResultPageDestination extends Component {
    componentWillUnmount() {
        this.props.updateMap([{none: "none"}]);
    }

    render() {
        return (
            <div
                className="EntireBox  container col-md-12  position-absolute bg-light"
                id="EntireBox_ResultDestination"
            >
                <div className="container ">
                    <AppViewHeader SearchState={"Real time Information"}/>
                </div>

        <div className='DestinationResult'>
          <h5 className="col-8 resultLabel  ">
            {this.props.match.params.start} to {this.props.match.params.end}
          </h5>
          <DataProvider
            endpoint="destination"
            updateMap={this.props.updateMap}
            startLat={this.props.match.params.startLat}
            startLon={this.props.match.params.startLon}
            destinationLat={this.props.match.params.destinationLat}
            destinationLon={this.props.match.params.destinationLon}
            time={this.props.match.params.startTimeToBackEnd}
            date={this.props.match.params.startDateToBackEnd}
            backend={this.props.backend}
            render={data => <Table data={data} />}
          />
        </div>
        <ResultPageButton markers={this.props.markers} polyline={this.props.polyline} />
      </div>
    );
  }

}

export default ResultPageDestination;
