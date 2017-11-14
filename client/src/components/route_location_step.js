import React from 'react'
import humanizeDuration from 'humanize-duration'
import NiceTime from './nice_time'

class RouteLocationStep extends React.Component {
  _renderWaitTime() {
    if (this.props.step.duration > 0) {
      return (
        <div>
          (wait { humanizeDuration(this.props.step.duration*1000, { units: ['m']}) })
        </div>
      );
    }
    return '';
  }

  _renderArrivalTime() {
    if (this.props.step.arrival_time && !this.props.step.departure_time) {
      return (
        <div>
          Arrival: <NiceTime dt={new Date(this.props.step.arrival_time)} />
        </div>
      );
    }
  }


  render() {
    const height = Math.max(15, this.props.step.duration / 10);
    return (
      <div className="routeLocationStepContainer">
        <div style={{height}} className="col routeLocationStepSymbol" />
        <div className="col routeLocationStepText">
          <div>
            {this.props.step.name} {this._renderWaitTime()}
          </div>
          {this._renderArrivalTime()}
        </div>
      </div>
    );
  }
}
export default RouteLocationStep;
