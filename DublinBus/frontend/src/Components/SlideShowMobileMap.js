import React, { Component } from "react";
import SlidingPane from "react-sliding-pane";
import "react-sliding-pane/dist/react-sliding-pane.css";
import "../Static/StyleSheet/SlideShowMobileMap.css";
import MobileMap from "./MobileMap";
import Modal from 'react-modal';

{
//    This component is used to display map for mobile user
//    used at ResultPageDestination, ResultPage_Stop_Route and Journey Planner_ResultPage
}

class ButtonAtResultPage extends Component {
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
      <div className="row container ShowMapAndFare position-relative "  ref={ref => this.el = ref}>

                <div className="col-8 d-md-none showMapButton">
                    <button className="btn btn-warning " onClick={() => this.setState({isPaneOpenLeft: true})}>Show
                        Map
                    </button>
                </div>

        <SlidingPane
          className="d-md-none"
          closeIcon={
            <a>
              <i className="fas fa-arrow-left"></i>
            </a>
          }
          isOpen={this.state.isPaneOpenLeft}
          title="Previous Page"
          from="right"
          width="100%"
          onRequestClose={() => this.setState({ isPaneOpenLeft: false })}
        >
          <MobileMap polyline={this.props.polyline} markers={this.props.markers}/>
        </SlidingPane>
      </div>
    );
  }
}

export default ButtonAtResultPage;
