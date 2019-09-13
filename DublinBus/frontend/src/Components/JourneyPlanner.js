import React, { Component } from "react";
import { Link } from "react-router-dom";
import "../Static/StyleSheet/SearchbyDestination.css";
import "../Static/StyleSheet/JourneyPlanner.css";
import AppViewHeader from "./AppViewHeader";
import AppViewFavourAndLogin from "./AppViewFavourAndLogin";
import YourLocationOrSearch from "./YourLocationOrSearch";
import JouneryPlanner_ToVisitPiont from "./JouneryPlanner_ToVisitPiont";
import JourneyPanner_SlideShow_List_DublinAttaction from "./JourneyPanner_SlideShow_List_DublinAttaction";
import JourneyPlanner_List_of_All_Tourist_Attraction from "./JourneyPlanner_List_of_All_Tourist_Attraction";
import axios from "axios";
import WarningAlert from "./WarningAlert";
import { Button, Accordion, Card } from "react-bootstrap";
import { addDays } from "date-fns";
import "bootstrap";
import * as $ from "jquery";

// npm install react-datepicker --save
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

//This Component is Search by Destination at the mobile view ports
class JourneyPlanner extends Component {
  constructor(props) {
    super(props);

    this.state = {
      initial_Date: null,
      initial_Time: null,

      startDateToBackEnd: null,
      startTimeToBackEnd: null,

      //Location Co-Ordinate start Here
      currentLocation_lat: null,
      currentLocation_long: null,

      startLat: "",
      startLon: null,
      home: null,

      PickedTouristAttraction: [],
      ListOfAllAttractions: [],
      submittedAttractions: [],

      bgColor: ["#F65314", "#7CBB00", "#00A1F1", "#FFBB00", "#146EB4"],

      warningText: "",
      useSearchLocation: true
    };

    this.updateCurrentPosition = this.updateCurrentPosition.bind(this);
    this.updateHome = this.updateHome.bind(this);

    this.setPosition = this.setPosition.bind(this);
    this.ToRemoveSelectedCardsFromListOfAllTouristCard_AfterSelect = this.ToRemoveSelectedCardsFromListOfAllTouristCard_AfterSelect.bind(
      this
    );
  }

  checkEmpty() {
    {
      //    To activate Warning alert
    }
    if (this.state.startLat.length == 0) {
      this.setState({
        warningText: "Please select a start point"
      });

      let $ = jQuery;

      (function($) {
        $("#JourneyPlannerWarning").modal("toggle");
      })(jQuery);
    } else if (this.state.PickedTouristAttraction.length == 0) {
      this.setState({
        warningText: "Please select a location to visit"
      });
      let $ = jQuery;

      (function($) {
        $("#JourneyPlannerWarning").modal("toggle");
      })(jQuery);
    } else {
      this.props.history.push(
        `/JourneyPlannerResultPage/${this.state.startLat}/${this.state.startLon}/${this.state.startDateToBackEnd}/${this.state.startTimeToBackEnd}/${this.state.submittedAttractions}/${this.state.home}`
      );
    }
  }

  updateHome(newHome) {
    this.setState({
      home: newHome
    });
  }

  componentDidMount() {
    {
      //Fetch list of attractions from server
    }

    axios({
      method: "get",
      url: this.props.backend + "attractions/",
      params: {
        route: this.state.routeNumber,
        direction: this.state.direction
      }
    })
      .then(response => {
        if (response.status !== 200) {
          return this.setState({ placeholder: "Something went wrong" });
        }
        return response.data;
      })
      .then(data =>
        this.setState({ ListOfAllAttractions: data, loaded: true })
      );
  }

  updateCurrentPosition(e) {
    this.setState({
      startLat: e.latitude,
      startLon: e.longitude,
      home: e.address
    });
  }


  setPosition(position) {
    {
      //This is Geolocation ask for current location
    }
    this.setState({
      currentLocation_lat: position.coords.latitude,
      currentLocation_long: position.coords.longitude
    });
  }

  ToRemoveSelectedCardsFromListOfAllTouristCard_AfterSelect(attraction) {
    {
      //    This Function is used to remove the card from List of all cards once it been add to to visit list
    }

    this.setState(prevState => ({
      ListOfAllAttractions: prevState.ListOfAllAttractions.filter(
        el => el.name != attraction.name
      )
    }));
  }

  AddAttactionCard(attractions) {
    {
      //    This function is for add card from the listed of Tourist Attraction into tourist to visit point components
    }
    if (this.state.PickedTouristAttraction.length <= 2) {
      this.setState(
        {
          PickedTouristAttraction: [
            ...this.state.PickedTouristAttraction,
            attractions
          ]
        },
        () => {
          this.ToRemoveSelectedCardsFromListOfAllTouristCard_AfterSelect(
            attractions
          );
        }
      );
      this.state.submittedAttractions.push(attractions.name);
    } else {
      //This is used to activate the alert box
      let $ = jQuery;

      (function($) {
        $("#JourneyPlannerAlertBox").modal("toggle");
      })(jQuery);
    }
  }

  ToAddCardBackToAllCardList(attractions) {
    {
      //    return the card back to all attraction card list after user that card from selected list
    }
    this.setState({
      ListOfAllAttractions: [...this.state.ListOfAllAttractions, attractions]
    });
  }

  removeAttractionFromSelected(attraction) {
    this.setState(
      prevState => ({
        PickedTouristAttraction: prevState.PickedTouristAttraction.filter(
          el => el.name != attraction.name
        )
      }),
      () => {
        this.ToAddCardBackToAllCardList(attraction);
      }
    );
    delete this.state.submittedAttractions[
      this.state.submittedAttractions.indexOf(attraction.name)
    ];
  }

  //    The two function below is used for managing button color (each selected attraction) for Picked Attraction
  _removeSelectedColorFromList(color) {
    {
      //    Remove color from list
    }

    this.setState(
      prevState => ({
        bgColor: prevState.bgColor.filter(el => el != color)
      }),
      () => this._AddBackSelectedColor(color)
    );
  }

  _AddBackSelectedColor(color) {
    {
      // re-append the color to end of the list
    }
    this.setState({ bgColor: [...this.state.bgColor, color] });
  }

  //End here - managing button color (each selected attraction) for Picked Attraction

  //This is Geolocation ask for current location
  setPosition(position) {
    this.setState({
      startLat: position.coords.latitude,
      startLon: position.coords.longitude
    });
  }

  //Ask for permission to obtain current locations
  getLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(this.setPosition);
    }
  }

  useCurrentLocation() {
    this.setState({ useSearchLocation: false });
    this.getLocation();
  }

  useSearchLocation() {
    this.setState({ useSearchLocation: true });
  }

  render() {

    return (
      <div>
        <div className="EntireBox  SearchByDestinationBox JoureyPlaner bg-light container col-md-12  position-absolute  ">
          <AppViewHeader SearchState={"Tourist Planner"} Return="toHomePage" />
          <AppViewFavourAndLogin />

          <div id="formColor">
            <form onSubmit={e => {e.preventDefault(); }}>
              <div className="container  SearchByDestinationForm">
                <div className="row  JourneyPlannerRowSecond">
                  {/*Start location starts here*/}
                  <div className="col-12 JourneyPlanerAddressLabel ">
                    <label> Start Point:</label>
                  </div>

                  <div className="col-10 JourneyPlanerInput ">
                    <YourLocationOrSearch
                      onUpdatePosition={this.updateCurrentPosition}
                      useCurrentLocation={this.useCurrentLocation.bind(this)}
                      useSearchLocation={this.useSearchLocation.bind(this)}
                      useuseSearchLocation_State={this.state.useSearchLocation}
                      id="JourneyPlannerStart"
                    />
                  </div>
                  {/*Start location Ends here*/}
                </div>

                <div className="col-12 listDestination_label  ">
                  <label> Selected Attractions:</label>
                </div>
                <div className="accordion" id="accordionExample">
                  <div className="row listDestination border border-white ">
                    {/*add to travel destination*/}
                    {this.state.PickedTouristAttraction.map(
                      (cardInfo, index) => (
                        <JouneryPlanner_ToVisitPiont
                          ref={this.getFunctionFromToVistPiont}
                          buttonID={`button_${index}`}
                          cardID={`attraction_${index}`}
                          key={index}
                          name={cardInfo.name}
                          image={cardInfo.img}
                          description={cardInfo.description}
                          removeAttractionFromSelected={this.removeAttractionFromSelected.bind(
                            this
                          )}
                          PickedAttractionButtonBgColor={
                            this.state.bgColor[index]
                          }
                          _AddBackSelectedColor={this._removeSelectedColorFromList.bind(
                            this
                          )}
                        />
                      )
                    )}
                  </div>
                </div>
                <Accordion>
                  <JourneyPanner_SlideShow_List_DublinAttaction
                    AddAttactionCardFunction={this.AddAttactionCard.bind(this)}
                    ListOfAllAttractions={this.state.ListOfAllAttractions}
                  />
                </Accordion>
              </div>
            </form>
          </div>

          <button
            type="button"
            className="btn btn-warning col-7"
            id="SubmitButton"
            onClick={this.checkEmpty.bind(this)}
          >
            Submit
          </button>
        </div>

        <Accordion className="ListofAllAttractions d-none d-lg-block ">
          <JourneyPlanner_List_of_All_Tourist_Attraction
            AddAttactionCardFunction={this.AddAttactionCard.bind(this)}
            ListOfAllAttractions={this.state.ListOfAllAttractions}
          />
        </Accordion>

        <WarningAlert
          color={"#146EB4"}
          id={"JourneyPlannerAlertBox"}
          title={"Information"}
          content={"Sorry, You can only select up to three attractions."}
        />
        <WarningAlert
          color={"#F65314"}
          id={"JourneyPlannerWarning"}
          title={"Warning"}
          content={this.state.warningText}
        />
      </div>
    );
  }
}

export default JourneyPlanner;
