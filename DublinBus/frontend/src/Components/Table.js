import React from "react";
import {
    FaWalking,
    FaLevelDownAlt,
    FaMapMarkerAlt,
    FaBus
} from "react-icons/fa";


{
//    This Component is used in Result Page Destination , For the purpose of displaying route instruction
}
const Table = ({data}) =>
    !data.length ? (
        <p>Nothing to show</p>
    ) : (
        <div>
            <div className="row "></div>

            <div className="container border border-primary">
                <div className="container ResultPageDestination  ">

                    <div>

                        <div className="row DestinationLabels  ">

                            <h5>Estimated Travel Time:  {data[0].duration}  mins</h5>

                        </div>
                    </div>



                    <div className="tab-content" id="pills-tabContent">
                        <div>
                            {data[0].directions.map((x, y) => (
                                //    Loop throught
                                <div key={y}>
                                    <div className="row instruction  ">
                                        <p className="Icons_ResultPage ">
                                            {x.travel_mode == "WALKING" ? (
                                                <FaWalking className="Icon"/>
                                            ) : (
                                                <FaBus className="Icon"/>
                                            )}
                                        </p>
                                        <p
                                            className="instruction_text"

                                        >
                                            {x.instruction}
                                        </p>
                                        <p className="time_show ">
                                            {x.time} mins
                                        </p>
                                    </div>
                                    <FaLevelDownAlt className="arrow_down_icon "/>

                                </div>
                            ))}

                            <div className="row result_destination  ">
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
            <div></div>
        </div>
    );

export default Table;
