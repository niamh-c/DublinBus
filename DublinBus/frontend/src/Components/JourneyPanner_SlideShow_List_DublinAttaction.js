import React, { Component } from "react";
import SlidingPane from "react-sliding-pane";
import "react-sliding-pane/dist/react-sliding-pane.css";
import "../Static/StyleSheet/SlideShowMobileMap.css";
import JourneyPlanner_List_of_All_Tourist_Attraction from "./JourneyPlanner_List_of_All_Tourist_Attraction";
import "bootstrap";
import Modal from 'react-modal';

{
  //this is the component will be appear at mobile version ,
  //What it does is show a button which user clicks and slide
  // show appears and show all the dublin tourist attraction
}
class JourneyPanner_SlideShow_List_DublinAttaction extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isPaneOpen: false,
      isPaneOpenLeft: false
    };
  }
  componentDidMount() {
        Modal.setAppElement(this.el);
    }
  render() {
    return (
      <div
        className="row  col-12  position-absolute ResultPageButton"
        id="JourneyPannerListBottom"
         ref={ref => this.el = ref}
      >
        <div className="d-lg-none   JourneyPannerListButton_">
          <a
            className="btn btn-warning "
            style={{ width: "auto" }}
            onClick={() => this.setState({ isPaneOpenLeft: true })}
          >
            Show All Attractions
          </a>
        </div>

        <SlidingPane
          className="d-lg-none col-sm-12"
          closeIcon={
            <a>
              <i className="fas fa-arrow-left"></i>
            </a>
          }
          isOpen={this.state.isPaneOpenLeft}
          title="All Dublin Attractions"
          from="right"
          width="100%"
          onRequestClose={() => this.setState({ isPaneOpenLeft: false })}
        >
          <div className=" MobileShowAllAttraction" id="CardAccordion">
            <JourneyPlanner_List_of_All_Tourist_Attraction
              AddAttactionCardFunction={this.props.AddAttactionCardFunction.bind(
                this
              )}
              ListOfAllAttractions={this.props.ListOfAllAttractions}
            />
          </div>
        </SlidingPane>
      </div>
    );
  }
}

export default JourneyPanner_SlideShow_List_DublinAttaction;
