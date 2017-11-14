import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/css/bootstrap-theme.css';
import 'font-awesome/css/font-awesome.min.css';
import WebFont from 'webfontloader';
import App from './App';
import registerServiceWorker from './registerServiceWorker';

WebFont.load({
    google: {
      families: ['VT323']
    }
  });

ReactDOM.render(<App />, document.getElementById('root'));
registerServiceWorker();
