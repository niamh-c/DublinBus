import React, { Component } from "react";
import "../Static/StyleSheet/AppViewFavourAndLogin.css";

{
  //This Component is the login and favour icon at the mobile view ports
}
class AppViewFavourAndLogin extends Component {
  render() {
    return (
      <div className="container AppView" style={appViewHeader}>
        <div className="row">
          <div
            className="col-3 "
            id="appViewLoginIcon"
            style={appViewLoginStyle}
          >
            <a>{/*<i className="fa fa-user"></i>*/}</a>
          </div>
          <div className="col-6 "></div>
          <div className="col-3 ">
            <a style={favourPageStyle} id="favourPage">
              {/*<i className="fa fa-heart"></i>*/}
            </a>
          </div>
        </div>
      </div>
    );
  }
}
const appViewHeader = {
  marginTop: "15px",
  marginBottom: "15px",
  backgroundColor: "light"
};
const appViewLoginStyle = {
  fontSize: "30px",

  margin: "auto"
};

const favourPageStyle = {
  fontSize: "24px",
  //
  display: "block",
  // margin:'auto',
  marginLeft: "30px",
  marginTop: "5px",
  color: "red"
};

export default AppViewFavourAndLogin;
