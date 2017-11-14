import React from 'react'

class NiceTime extends React.Component {

  render() {
    const dt = this.props.dt;
    const hours = dt.getHours();
    const mins = dt.getMinutes();
    let str = hours + ':';
    if (mins < 10) {
      str += '0';
    }
    str += mins;
    if (hours < 12) {
      str += ' am';
    } else {
      str += ' pm';
    }
    return str;
  }
}
export default NiceTime;
