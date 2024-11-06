import React, { Component } from 'react';
import TitleBar from './TitleBar';
import TileGrid from './TileGrid';

class SiaDashboardRemote extends Component {
  render() {
    return (
      <div className="App">
        {/* <TitleBar
          title="Well #1"
          tankLevel="75%"
          actualFlowRate="120.2 L/min"
          targetFlow="119 L/min"
          pressureDelta="5 bar"
          strokesPerMin="30"
          hasFault={true} // Set this to true or false to see the flashing effect
        /> */}
        <TileGrid />
      </div>
    );
  }
}

export default SiaDashboardRemote;
