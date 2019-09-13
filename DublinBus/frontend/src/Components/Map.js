import React, {Component, setState} from "react";
import marker from '../Static/img/marker.png'
import {IoMdLocate} from "react-icons/io";


import {
    withGoogleMap,
    GoogleMap,
    Marker,
    InfoWindow,
    Polyline
} from "react-google-maps";
import "../Static/StyleSheet/Map.css";

class Map extends Component {

    constructor(props) {
        super(props);
        this.state = {
            lat: 0,
            long: 0,
            defaultCenter_lat: 53.3501,
            defaultCenter_long: -6.2661,

        };

        this.getLocation = this.getLocation.bind(this);
        this.setPosition = this.setPosition.bind(this);
    }


    setPosition(position) {
        let lat = Number(position.coords.latitude)
        let long = Number(position.coords.longitude)

        this.setState({

            lat: lat,
            long: long,
            defaultCenter_lat: lat,
            defaultCenter_long: long,
        });
    }

    //Ask for permission to obtain current locations
    getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(this.setPosition);
        }
    }

    render() {
        {
            /* Creates the marker if it is in the markers array(state)
                     We only want this to update when markers state is updated.*/
        }
        const MapWithAMarker = withGoogleMap(props => (
            <GoogleMap
                defaultZoom={11}
                defaultCenter={{
                    lat: 53.3501,
                    lng: -6.2661
                }}
                defaultOptions={{
                    disableDefaultUI: true
                }}
            >
                <Polyline
                    path={this.props.polyline}
                    strokeColor="#0000FF"
                    strokeOpacity={0.8}
                    strokeWeight={2}
                />
                {this.props.markers.map((x, y) => (
                    <Marker
                        key={y}
                        position={{
                            lat: x.lat,
                            lng: x.lng
                        }}
                    />
                ))}

                <Marker
                    position={{lat: this.state.lat, lng: this.state.long}}
                    animation={window.google.maps.Animation.DROP}
                    icon={marker}
                />
            </GoogleMap>
        ));

        return (
            <div className={`position-relative ${this.props.showMap}` } id="map">
                <div className='currentLocationIcon_map position-fixed'><a onClick={this.getLocation}>
                    <IoMdLocate className="icon_map_1 " size={35}/>
                </a></div>

                <MapWithAMarker
                    containerElement={
                        <div style={{height: `100vh`, width: "100%"}}/>
                    }
                    mapElement={<div style={{height: `100%`}}/>}
                />


            </div>
        );
    }
}

export default Map;
