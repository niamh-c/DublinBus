import React from "react";
import Map from "./Map";
import {IoMdLocate} from "react-icons/io";
import '../Static/StyleSheet/MobileMap.css'

{
//    Display map for mobile user
//    Used at result page search by route stop and destination
}
class mobileMap extends React.Component {
    constructor(props) {
        super(props);

        this.child = React.createRef();


        this.onclickFindLocation = this.onclickFindLocation.bind(this);


    }


    onclickFindLocation() {
        this.child.current.getLocation();
    }


    render() {
        return (

            <div className="container col-12 position-relative MobileMap">
                <Map ref={this.child} markers={this.props.markers} polyline={this.props.polyline} />

                <div className='currentLocationIcon position-fixed' ><a
                    onClick={this.onclickFindLocation}>
                    <IoMdLocate className="icon_map " size={35}/>
                </a></div>


            </div>
        );
    }
}

export default mobileMap;
