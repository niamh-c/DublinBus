import React from "react";
import GoogleAddressSearch from "./GoogleAddressSearch";
import "../Static/StyleSheet/YourLocationOrSearch.css";
import {OverlayTrigger,  Tooltip} from 'react-bootstrap';


//This component is uses to provided option for user whether if they want to use current location or
        //search to choice for it own start point
//This Component is used in the Component Search by Destination and Tourist Journey Planner
import {FaCrosshairs, FaSearchLocation} from "react-icons/fa";
class YourLocationOrSearch extends React.Component {
    constructor(props) {
        super(props);
        this.state = {inputText: "From Your Current Location"};


    }


    renderInputField() {
        if (this.props.useuseSearchLocation_State == true) {
            return (
                <div>
                    <GoogleAddressSearch
                        comment="Set Your Start Point"
                        onUpdatePosition={this.props.onUpdatePosition}
                        id={this.props.id}
                    />
                </div>
            );
        } else {
            return (
                <input
                    id="InputBoxYourLocationOrSearch"
                    value={this.state.inputText}
                    disabled
                />
            );
        }
    }

    renderButton() {

        let button;

        if (this.props.useuseSearchLocation_State == true) {

            button = (


                <div>
                    <OverlayTrigger
                        overlay={<Tooltip className='Tooltip'>Click Icon,Set your Current Location as Start Point </Tooltip>}>

                        <a onClick={this.props.useCurrentLocation}>
                            <FaCrosshairs className="icon"/>
                        </a>

                    </OverlayTrigger>


                </div>
            );
        } else {
            button = (
                <OverlayTrigger
                    overlay={<Tooltip  className='Tooltip' >Click Icon,to Search and Pick for Your Start Point</Tooltip>}>
                    <a  onClick={this.props.useSearchLocation}>
                        <FaSearchLocation className="icon"/>
                    </a>
                </OverlayTrigger>
            );
        }

        return button;
    }


    render() {
        return (
            <div  className="row">
                <div className="col-10 ">{this.renderInputField()}</div>
                <div className="col-2  ClickChangeInput">{this.renderButton()}</div>
            </div>
        );
    }
}


export default YourLocationOrSearch;
