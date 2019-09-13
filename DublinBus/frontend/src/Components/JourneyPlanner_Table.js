import React, { Component } from "react";
import "../Static/StyleSheet/JourneyPlanner_Table.css";
import DataProvider from "./DataProvider";
import {Button, Accordion, Card} from 'react-bootstrap';
import JourneyPlannerRouteTable from "./JourneyPlannerRouteTable";

{
//    Display of User selected Destination Point
//    Used at Component JourneyPlannerResultDisplay
}
class JourneyPlanner_Table extends React.Component {
  constructor (props) {
    super(props);
    this.state = {
      startLat: this.props.startLat,
      startLon:this.props.startLon,
      destinationLat: this.props.destinationLat,
      destinationLon: this.props.destinationLon,
      route: "",
    }
    this.displayRoute = this.displayRoute.bind(this);
  }

updateTimeTwo(newtime) {
  this.setState({
      timeTwo: newTime,
  })
}

updateTimeThree(newtime) {
  this.setState({
      timeThree: newTime,
  })
}

updateTimeThree(newtime) {
  this.setState({
      timeThree: newTime,
  })
}

displayRoute() {
    if (this.state != ""){
      this.props.updateMap([{ none: "none" }]);
    }
    this.setState({
        route: this.state.route == "" ?
            <DataProvider
            endpoint="destination"
            updateMap={this.props.updateMap}
            startLat={this.state.startLat.toString()}
            startLon={this.state.startLon.toString()}
            destinationLat={this.state.destinationLat.toString()}
            destinationLon={this.state.destinationLon.toString()}
            backend={this.props.backend}
            render={data => <JourneyPlannerRouteTable data={data} color={this.props.color}/>}
          /> : ""
    })
}
  render() {
    const color = this.props.color;
    return (
      <React.Fragment>
        <Accordion>
                <div className=" resultDisplay">

                    <Accordion.Toggle className=' JourneyPlanner_Table '
                                      style={{borderTop: `5px solid ${color}`}}
                                      as={Button} variant="link"
                                      eventKey={this.props.number}
                                      onClick={this.displayRoute}>
                        <div className='row' >

                            <div className=' NumberContainer ' >
                                <div className=' position-relative ShowOrders  '
                                     style={{backgroundColor: color}}>
                                    <p className='NumberingOrders  position-absolute '>{this.props.number}</p>

                                </div>
                            </div>
                                    <h5 className='AttractionName'
                                        style={{color: this.props.color}}>{this.props.attraction}</h5>
                                </div>
                    </Accordion.Toggle>
                </div>



                    <Accordion.Collapse  eventKey={this.props.number}
                    >
                        <div>{this.state.route}</div>
                    </Accordion.Collapse>
                    </Accordion>


      </React.Fragment>
    );
  }
}

export default JourneyPlanner_Table;
