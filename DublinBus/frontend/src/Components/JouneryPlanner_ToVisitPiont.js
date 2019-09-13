import React from "react";

{
    //This is Component is the attraction that tourist selected and planed to visit
}
class JouneryPlanner_ToVisitPiont extends React.Component {
  render() {
    return (
      <React.Fragment>
        {/*This the the button shown on Journey Planner page , after a user pick the attraction to visit*/}
        <a
          className="btn  btn-success border border-secondary "
          id={this.props.buttonID}
          style={{ backgroundColor: this.props.PickedAttractionButtonBgColor }}
          data-toggle="modal"
          href={`#${this.props.cardID}`}
          aria-expanded="false"
        >
          <p>
            <i className="fab fa-fort-awesome-alt "></i>
          </p>
        </a>

        {/*This is the model (initialy hidden , will shows after above clicked above button) ,
             contains a card which indicates the information of each selected attraction*/}
        <div
          className="modal fade "
          id={this.props.cardID}
          role="dialog"
          aria-labelledby="exampleModalCenterTitle"
          aria-hidden="true"
        >
          <div className="modal-dialog  modal-dialog-centered" role="document">
            <div className="modal-content">
              <div className="modal-header border border-success">
                <h4 className="modal-title" id="exampleModalLongTitle">
                  {this.props.name}
                </h4>

                {/*This is exit button , click to close the model*/}
                <button
                  type="button"
                  className="close  border border-success"
                  data-dismiss="modal"
                  aria-label="Close"
                >
                  X
                </button>
              </div>
              <div className="card">

                <div className="card-body">
                  <p className="card-text">{this.props.description}</p>
                </div>
              </div>

              {/*Button to remove the card from the selected list*/}
              <button
                type="button"
                className="Delete_bottom btn btn-info col-6"
                data-dismiss="modal"
                onClick={() => {
                  this.props.removeAttractionFromSelected({
                    name: this.props.name,
                    description: this.props.description,
                    href: this.props.image
                  });
                  this.props._AddBackSelectedColor(
                    this.props.PickedAttractionButtonBgColor
                  );
                }}
              >
                Remove selected attraction?
              </button>
            </div>
          </div>
        </div>
      </React.Fragment>
    );
  }
}

export default JouneryPlanner_ToVisitPiont;
