import React, {Component} from "react";
import PropTypes from "prop-types";
import axios from "axios";
import loading from "../Static/img/loading.gif";

const imgStyle = {
    leftMargin: "auto",
    rightMargin: "auto"
};

{
    /*Handling Get and Post*/
}
class DataProvider extends Component {
    static propTypes = {
        render: PropTypes.func.isRequired,
        endpoint: PropTypes.string.isRequired,
        stopnumber: PropTypes.string,
        route: PropTypes.string,
        towards: PropTypes.string,
        destinationLat: PropTypes.string,
        destinationLon: PropTypes.string,
        startLat: PropTypes.string,
        startLon: PropTypes.string,
        destination: PropTypes.string,
        time: PropTypes.string,
        date: PropTypes.string,
        attractions: PropTypes.string,
        home: PropTypes.string
    };
    state = {
        data: [],
        loaded: false,
        placeholder: (
            <img src={loading} alt="loading..." width="120" height="120"/>
        ),
    };

    componentDidMount() {
        axios({
            method: "get",
            url: this.props.backend + this.props.endpoint + "/",
            params: {
                stopnumber: this.props.stopnumber,
                route: this.props.route,
                towards: this.props.towards,
                destinationLat: this.props.destinationLat,
                destinationLon: this.props.destinationLon,
                startLat: this.props.startLat,
                startLon: this.props.startLon,
                time: this.props.time,
                date: this.props.date,
                attractions: this.props.attractions,
                home: this.props.home
            }
        })
            .then(response => {
                if (response.data.length == 0) {
                    this.setState({placeholder: "No routes possible at this time"});
                    return;
                } else {
                    this.props.updateMap(response.data);

                    this.setState({data: response.data, loaded: true});
                    return;
                }
            })
            .catch(error => {
                if (error.response) {
                    this.setState({placeholder: "No routes possible at this time"});
                } else if (error.request) {
                    this.setState({placeholder: "The server is not available at this time"});
                }
            });
    }

    render() {
        const {data, loaded, placeholder} = this.state;
        return loaded ? this.props.render(data) : <p>{placeholder}</p>;
    }

}

export default DataProvider;
