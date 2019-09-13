import React, {Component} from "react";
import JourneyPlanner_Table from "./JourneyPlanner_Table";

class JourneyPlannerResultsDisplay extends Component {
    constructor(props) {
        super(props);
    }

    componentWillUnmount() {
        this.props.updateMap([{none: "none"}]);
    }

    render() {
        const color = ["#F65314", "#7CBB00", "#00A1F1", "#FFBB00", "#146EB4", "#EA4335"];
        return this.props.data.map((x, y) => (
            <div className="accordion" id="accordionExample" key={y}>
                <JourneyPlanner_Table
                    number={x.number}
                    buttonID={`ResultPageButton_${x.number}`}
                    cardID={`AttractionStop_${x.number}`}
                    attraction={x.attraction}
                    description={x.description}
                    color={color[x.number]}
                    startLat={x.start_lat}
                    startLon={x.start_lon}
                    destinationLat={x.end_lat}
                    destinationLon={x.end_lon}
                    updateMap={this.props.updateMap}
                    backend={this.props.backend}
                />
            </div>
        ));
    }
}

export default JourneyPlannerResultsDisplay;
