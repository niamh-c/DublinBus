import React from "react";
import key from "weak-key";
import "../Static/StyleSheet/ResultPage_Stop_Route.css";


{
//  Display of result for Search by Route and Stop
}

const ResultTable_StopRoute = props => {
  const { data } = props;

  return (
    <div className="ResultTableStopRoute">
      {props.data[0].directions.map((x, y) => (
        //    Loop throught
        <div className="row resultRows" key={y}>
          <div className="col-4 busNumber">
            <p >{x.instruction}</p>
          </div>
          <div className="col-6 busArrivalTime ">
            <p >{x.time}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ResultTable_StopRoute;
