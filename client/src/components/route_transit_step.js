import React from 'react'
import FontAwesome from 'react-fontawesome'
import humanizeDuration from 'humanize-duration'
import NiceTime from './nice_time'

class RouteTransitStep extends React.Component {

  getIconName() {
    const icons = {
      train: 'subway',
      shuttle: 'bus',
      walk: 'street-view'
    }
    return icons[this.props.step.type];
  }

  render() {
    const height = this.props.step.duration / 10;
    return (
      <div style={{height}} className="routeTransitStepContainer">
        <div style={{borderColor: '#DD0000'}} className="col routeTransitStepSymbol" />
        <FontAwesome className='col' size='lg' name={this.getIconName()} />
        <div className="col routeTransitStepText">
          <div>
            Departure: <NiceTime dt={new Date(this.props.step.departure_time)} /> 
          </div>
          <div>
            {humanizeDuration(this.props.step.duration*1000)}
          </div>
        </div>
      </div>
    );
  }
}
export default RouteTransitStep;
