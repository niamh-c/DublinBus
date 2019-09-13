import React, { Component } from "react";
import Script from "react-load-script";

// npm i react-load-script --save
let google = window.google;

{
//  For Google Address Search ,
//  Displayed at Search by Destination and Journey Planner
//  Used in the Component YourLocationOrSearch
}
class GoogleAddressSearch extends Component {
  componentDidMount() {
    const inputEl = document.getElementById(this.props.id);

    //set Bound
    let defaultBounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(53.281561, -6.364376),
      new google.maps.LatLng(53.400044, -6.215727)
    );

    /*global google*/
    let options = {
      bounds: defaultBounds,
      //types: ['address'],
      componentRestrictions: { country: "ie" }
    };

    this.autocomplete = new google.maps.places.Autocomplete(inputEl, options);
    this.autocomplete.addListener(
      "place_changed",
      this.handlePlaceSelect.bind(this)
    );
  }

  //pass geolocation via lat & long back to Search by Destination

  handlePlaceSelect() {
    this.props.onUpdatePosition({
      latitude: this.autocomplete.getPlace().geometry.location.lat(),
      longitude: this.autocomplete.getPlace().geometry.location.lng(),
      address:
        this.autocomplete.getPlace().address_components[0].short_name +
        " " +
        this.autocomplete.getPlace().address_components[1].short_name,
      home: this.autocomplete.getPlace().address_components[0].short_name
    });
  }

  render() {
    return (
      <section>


        <div className="form-group">
          <input
            type="text"
            autoComplete="new-password"
            className="form-control"
            id={this.props.id}
            name="address"
          />
        </div>
      </section>
    );
  }
}

export default GoogleAddressSearch;
