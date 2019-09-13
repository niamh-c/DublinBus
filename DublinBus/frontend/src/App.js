import React, {Component} from "react";
import {BrowserRouter as Router, Switch, Route} from "react-router-dom";
import SearchByStop from "./Components/SearchByStop";
import SearchbyDestination from "./Components/SearchbyDestination";
import HomePage from "./Components/HomePage";
import JourneyPlanner from "./Components/JourneyPlanner";
import ResultPage_Stop_Route from "./Components/ResultPage_Stop_Route";
import ResultPageDestination from "./Components/ResultPageDestination";
import JourneyPlannerResultPage from "./Components/JourneyPlaner_ResultPage";
import Map from "./Components/Map";
import MobileMap from "./Components/MobileMap";
import "./App.css";

class App extends Component {
    constructor() {
        super();
        this.state = {
            polyline: [],
            markers: [],
            backend: "https://route13.eu/api/",
            //backend: "http://localhost:8000/api/"
        };
        this.updateMap = this.updateMap.bind(this);
    }

    updateMap = newMapInfo => {
        this.setState({
            polyline: newMapInfo[0].hasOwnProperty("map")
                ? newMapInfo[0].map.polyline
                : []
        });
        this.setState({
            markers: newMapInfo[0].hasOwnProperty("map")
                ? newMapInfo[0].map.markers
                : []
        });
    };

    render() {
        return (
            <Router>

                <div className="App">
                    <div className="container-fluid position-relative appContainer">
                        <Map polyline={this.state.polyline} markers={this.state.markers} showMap=' d-none d-md-block'/>

                        <Switch>
                            <Route path="/" exact={true} component={HomePage}/>
                            <Route
                                path="/SearchByDestination"
                                render={({updateMap, match, history}) => (
                                    <SearchbyDestination
                                        updateMap={this.updateMap}
                                        match={match}
                                        history={history}
                                    />
                                )}
                            />
                            <Route path="/SearchByStop" component={SearchByStop}/>
                            <Route path="/JourneyPlanner"
                                render={({updateMap, match, history}) => (
                                    <JourneyPlanner
                                        match={match}
                                        history={history}
                                        backend={this.state.backend}
                                    />
                                )}
                            />
                            <Route
                                path="/ResultPage_Stop_Route/:stopnumber/:route"
                                render={({updateMap, match}) => (
                                    <ResultPage_Stop_Route
                                        updateMap={this.updateMap}
                                        match={match}
                                        polyline={this.state.polyline}
                                        markers={this.state.markers}
                                        backend={this.state.backend}
                                    />
                                )}
                            />
                            <Route
                                path="/JourneyPlannerResultPage/:startLat/:startLon/:startDateToBackend/:startTimeToBackend/:PickedTouristAttraction/:home"
                                render={({updateMap, match}) => (
                                    <JourneyPlannerResultPage
                                        updateMap={this.updateMap}
                                        match={match}
                                        polyline={this.state.polyline}
                                        markers={this.state.markers}
                                        backend={this.state.backend}
                                    />
                                )}
                            />

                            <Route
                                path="/ResultPageDestination/:startLat/:startLon/:destinationLat/:destinationLon/:startDateToBackEnd/:startTimeToBackEnd/:start/:end"
                                render={({updateMap, match}) => (
                                    <ResultPageDestination
                                        updateMap={this.updateMap}
                                        match={match}
                                        polyline={this.state.polyline}
                                        markers={this.state.markers}
                                        backend={this.state.backend}
                                    />
                                )}
                            />
                            {/*<Route component={NoPathToRender_ThenThisPage} />*/}
                        </Switch>
                    </div>
                </div>
            </Router>
        );
    }
}

export default App;
