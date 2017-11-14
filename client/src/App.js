import React, { Component } from 'react';
import './App.css';
import axios from 'axios';
import Route from './components/route'
import Config from './config'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      destination: '',
      origin: '',
      routes: [],    
    }
  }

  _renderRouteEntries() {
    let idx = 0;
    return this.state.routes.map((route) => {
      const now = new Date();
      if (new Date(route.steps[0].departure_time) > now && idx < 10) {
        idx++;
        return <Route key={idx} route={route} />;
      }
      return null;
    })
  }

  render() {
    return (
      <div className="App">
        <div className="routeContainer">
          {this._renderRouteEntries()} 
        </div>
      </div>
    );
  }
  
  loadData() {
    const config = new Config();
    let uri = config.route_server_proto;
    uri += '://' + config.route_server + '/routes';
    uri += window.location.pathname;
    console.log(uri);
    axios.get(uri)
      .then(
        (result) => {
          this.setState(result.data)
        });
  }
 
  componentDidMount() {
    this.loadData();
    // load data every 5 mins
    setInterval(this.loadData, 5*60*1000);
  }
}

export default App;
