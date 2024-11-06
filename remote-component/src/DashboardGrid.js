import React from 'react';
import { Grid } from '@mui/material';
import TitleBar from './WellTile';

const DashboardGrid = () => {
  // Sample data for the six tiles
  const tileData = [
    { title: 'Skid 1', tankLevel: 50, actualFlowRate: 4.49, targetFlow: 4.4, pressureDelta: 5, strokesPerMin: 60, hasFault: false },
    { title: 'Skid 2', tankLevel: 30, actualFlowRate: 4.20, targetFlow: 4.19, pressureDelta: 4, strokesPerMin: 55, hasFault: true },
    { title: 'Skid 3', tankLevel: 70, actualFlowRate: 3.92, targetFlow: 3.9, pressureDelta: 6, strokesPerMin: 70, hasFault: false },
    { title: 'Skid 4', tankLevel: 60, actualFlowRate: 3.82, targetFlow: 3.8, pressureDelta: 5, strokesPerMin: 65, hasFault: true },
    { title: 'Skid 5', tankLevel: 80, actualFlowRate: 4.97, targetFlow: 5, pressureDelta: 3, strokesPerMin: 75, hasFault: false },
    { title: 'Skid 6', tankLevel: 45, actualFlowRate: 4.43, targetFlow: 4.4,  pressureDelta: 4, strokesPerMin: 50, hasFault: true },
  ];

  return (
    <Grid container spacing={2}>
      {tileData.map((tile, index) => (
        <Grid item xs={12} sm={6} md={6} key={index}>
          <TitleBar
            title={tile.title}
            tankLevel={tile.tankLevel}
            actualFlowRate={tile.actualFlowRate}
            targetFlow = {tile.targetFlow}
            pressureDelta={tile.pressureDelta}
            strokesPerMin={tile.strokesPerMin}
            hasFault={tile.hasFault}
          />
        </Grid>
      ))}
    </Grid>
  );
};

export default DashboardGrid;
