import Imgx from "../Static/img/img1.webp";
import React from "react";
import "../Static/StyleSheet/JourneyPlanner_Card.css";
import { Button, Accordion, Card } from "react-bootstrap";

{
  //This is a card component which display attraction.
}
class JourneyPlanner_Card extends React.Component {
  render() {
    return (
      <div>
        <div className="card col-12 Card_allAttraction">
          <img
            className="card-img-top"
            src={this.props.href}
            alt="Card image cap"
          />

          <div className="cardBody">
            <Accordion.Toggle
              as={Button}
              variant="link"
              eventKey={this.props.buttonID}
            >
              <div className="row">
                <h5>{this.props.name}</h5>
              </div>
            </Accordion.Toggle>

            <div className="row ">
              <Accordion.Collapse eventKey={this.props.buttonID}>
                <Card.Body>
                  <p className="card card-text ">{this.props.description}</p>
                </Card.Body>
              </Accordion.Collapse>
            </div>
          </div>

          <a
            type="button"
            className=" btn btn-success col-6"
            onClick={this.props.AddAttactionCardFunction.bind(this, {
              name: this.props.name,
              description: this.props.description,
              img: this.props.href
            })}
          >
            <p>
              <i className="fas fa-plus"></i>
            </p>
          </a>
        </div>
      </div>
    );
  }
}

export default JourneyPlanner_Card;
