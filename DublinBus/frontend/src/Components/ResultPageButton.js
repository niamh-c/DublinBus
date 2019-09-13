import React, { Component } from "react";

import "../Static/StyleSheet/ResultPageButton.css";

{
    //This the Submit button for the Result page of the Search by Destination
}
class ButtonAtResultPage extends Component {
  render() {
    return (
      <div className="row container ResultPageButton  ">
        <div className="col-6   ">
          <button className=" btn btn-warning ">Show Fare</button>
        </div>
        <div className="col-6 y">
          <button className="btn btn-warning ">Show Map</button>
        </div>
      </div>
    );
  }
}

export default ButtonAtResultPage;
