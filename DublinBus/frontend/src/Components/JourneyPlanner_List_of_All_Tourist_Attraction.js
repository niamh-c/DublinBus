import React, { Component } from "react";
import Cards from "./JourneyPlanner_Card";


{
//  List of aLL Dublin's Attractions
//User At Journey Planner , Will only display for those computer user.
}
class JourneyPlanner_List_of_All_Tourist_Attraction extends Component {
  render() {
    return (
      <React.Fragment>
        {this.props.ListOfAllAttractions.map((cardInfo, Index) => (
          <Cards
            key={Index}
            name={cardInfo.name}
            href={cardInfo.image ? "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&key=AIzaSyDBnVde8R4LpYQapr6-zbAHPD5Xcva9H_c&photo_reference=" + cardInfo.image : cardInfo.href}
            description={cardInfo.description}
            buttonID={`CardButton_${Index}`}
            cardID={`CardAttraction_${Index}`}
            AddAttactionCardFunction={this.props.AddAttactionCardFunction.bind(
              this
            )}
          />
        ))}
      </React.Fragment>
    );
  }
}

export default JourneyPlanner_List_of_All_Tourist_Attraction;
