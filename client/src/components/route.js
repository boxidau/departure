import React from 'react';
import RouteTransitStep from './route_transit_step';
import RouteLocationStep from './route_location_step';
import format from 'format-duration'

class Route extends React.Component {

  MAX_TIME_BEFORE_DEPARTURE = 12*3600*1000; // 12 hours

  constructor(props) {
    super(props);
    this.state = {
      ttd: this.calculateTTD(),
      // for debugging
      enableTick: true
    };
  }

  _renderTripDuration() {
    return format(this.props.route.total_duration*1000);
  }

  calculateTTD() {
    const departure = new Date(this.props.route.steps[0].departure_time)
    const now = new Date();
    return departure - now;
  }  
  
  componentDidMount() {
    this.timerID = setInterval(
      () => {
        if (this.state.enableTick) {
          this.setState({ttd: this.calculateTTD()})
        }
      },
      500
    );
  }
  
  _renderTimeUntilDeparture() {
    const THRESHOLD = 10*60*1000;
    let redness = 0;
    if (this.state.ttd < THRESHOLD) {
      redness = Math.floor((THRESHOLD - this.state.ttd)/THRESHOLD*255);
    }
    const color = 'rgb(' + redness + ', 0, 0)';
    return <div className='countdownTimer' style={{color}}>{format(this.state.ttd)}</div>;
  }

  _renderRouteSteps() {
    let idx = 0;
    return this.props.route.steps.map((step) => {
      idx++;
      if (step.type !== 'location') {
        return (
            <RouteTransitStep key={idx} step={step} /> 
        )
      } else {
        return <RouteLocationStep key={idx} step={step} />;
      }
    })
  }

  render() {
    if (this.state.ttd < 0
        || this.state.ttd > this.MAX_TIME_BEFORE_DEPARTURE) {
      return null;
    }
    return (
        <div className="route">
          {this._renderTimeUntilDeparture()}
          <div>
            {this._renderRouteSteps()}
          </div>    
          Duration: {this._renderTripDuration()} <br />
        </div>
    );
  }
} 

export default Route;
