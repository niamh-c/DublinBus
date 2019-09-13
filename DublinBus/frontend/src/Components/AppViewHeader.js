import React, { Component } from "react";
import "../Static/StyleSheet/AppViewHeader.css";

{
  // This Component is a header at the mobile view
}

class AppViewHeader extends Component {
  constructor(props) {
    super(props);
    this.returnBack = this.returnBack.bind(this);
  }
  returnBack() {
    //Return to previous page and ensure the weather widget to load.
    if (this.props.Return === "toHomePage") {
      return window.location.replace("/");
    } else {
      return window.history.go(-1);
    }
  }
  render() {
    return (
      <div className="container AppViewHeader ">
        <div className="row ">
          <div className="col-2 ">
            {/*Return to previous component */}
            <a id="returnButton" onClick={this.returnBack}>
              <i className="fas fa-arrow-left"></i>
            </a>
          </div>

          <div className="col-8 ">
            <h5>{this.props.SearchState}</h5>
          </div>

          <div
            className="col-2 container AppViewDropDown  position-relative"
            id="AppViewDropDown"
          >
            {/*<DropDownINav />*/}
            <a onClick={() => window.location.replace("/")}>
              <p>
                <i className="fas fa-home"></i>
              </p>

            </a>
          </div>
        </div>
      </div>
    );
  }
}

export default AppViewHeader;
