import React from "react";
import {
    FaWalking,
    FaLevelDownAlt,
    FaMapMarkerAlt,
    FaBus
} from "react-icons/fa";

{
//    Display route Instruction at Result page Journey Planner
}
const JourneyPlannerRouteTable = ({data}) =>
    !data.length ? (
        <p>Nothing to show</p>
    ) : (
        <div>
            <div className="container JourneyPlannerResultDisplay  "

            >

                <div className="tab-content" id="pills-tabContent">
                    <div
                        className="tab-pane fade show active"
                        id="pills-home"
                        role="tabpanel"
                        aria-labelledby="pills-home-tab">
                        {data[0].directions.map((x, y) => (
                            //    Loop throught
                            <div  key={y}>
                                <div className="row instruction ">
                                    <p className="Icons_ResultPage ">
                                        {x.travel_mode == "WALKING" ? (
                                            <FaWalking className="Icon"/>
                                        ) : (
                                            <FaBus className="Icon"/>
                                        )}
                                    </p>
                                    <p
                                        className="instruction_text "

                                    >
                                        {x.instruction}
                                    </p>
                                    <p className="time_show " >
                                        {x.time} mins
                                    </p>
                                </div>
                                <FaLevelDownAlt className="arrow_down_icon "/>
                            </div>
                        ))}


                            <div className="row result_destination  " >
                                <p className="Icons_destination ">
                                    <FaMapMarkerAlt className="Icon"/>
                                </p>

                                <p className="destination_text ">
                                    Your Destination
                                </p>
                            </div>
                    </div>


                </div>

            </div>

        </div>
    );

export default JourneyPlannerRouteTable;