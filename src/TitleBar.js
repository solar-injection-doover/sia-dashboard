import React, { useEffect, useState, useRef } from 'react';
import { Box, Typography, Paper, Grid, Collapse, Button } from '@mui/material';
import { Circle, ExpandMore, ExpandLess } from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, LineElement, CategoryScale, LinearScale, PointElement } from 'chart.js';
import './TitleBar.css'; // Optional CSS for styling

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement);

const TitleBar = ({ title, tankLevel, actualFlowRate, targetFlow, pressureDelta, strokesPerMin, hasFault }) => {
  const [flashing, setFlashing] = useState(false);
  const [showFaults, setShowFaults] = useState(hasFault);
  const [showPlot, setShowPlot] = useState(false);
  const chartRef = useRef(null);

  useEffect(() => {
    if (showPlot) {
      const interval = setInterval(() => {
        setChartData(prevChartData => ({
          ...prevChartData,
          datasets: [
            {
              ...prevChartData.datasets[0],
              data: generateRandomData,
            },
          ],
        }));
      }, 600000); // Update every 10 minutes
      return () => clearInterval(interval);
    }
  }, [showPlot]);

  const generateRandomData = useRef(Array.from({ length: 30 }, () => Math.random() + 3.5)).current;

  const generateTimeLabels = () => {
    const labels = [];
    const currentDate = new Date();
    currentDate.setMinutes(currentDate.getMinutes() - 290); // Start 290 minutes ago for 30 points, 10 minutes each
    for (let i = 0; i < 30; i++) {
      labels.push(currentDate.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit', hour12: false }));
      currentDate.setMinutes(currentDate.getMinutes() + 10);
    }
    return labels;
  };

  const [chartData, setChartData] = useState({
    labels: generateTimeLabels(),
    datasets: [
      {
        label: 'Flow Rate over Time',
        data: generateRandomData,
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderWidth: 1,
      },
    ],
  });

  const chartOptions = {
    scales: {
      y: {
        title: {
          display: true,
          text: 'Flow Rate (L/Hr)',
        },
        min: 0,
        max: 5,
        ticks: {
          stepSize: 1,
        },
      },
    },
    responsive: true,
    maintainAspectRatio: false,
  };

  return (
    <Paper 
      className="title-bar"
      elevation={3}
      sx={{ padding: 2, textAlign: 'center', maxWidth: 400, margin: '0 auto', position: 'relative' }}
    >
      <Box className="watermark" sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%) rotate(-45deg)',
          color: 'rgba(0, 0, 0, 0.1)',
          fontSize: '4em',
          fontWeight: 'bold',
          pointerEvents: 'none',
          userSelect: 'none'
        }}
      >
        CONCEPT ONLY
      </Box>
      <Box display="flex" alignItems="center" justifyContent="space-between">
        <Box display="flex" alignItems="left" flexDirection="column">
            <Typography variant="h3" sx={{ fontSize: '1.55em', textAlign: 'left' }}>
            {title}
            </Typography>
            <Box display="flex" alignItems="center" sx={{ mt: "-3px", textAlign: 'left' }}>
                <Circle 
                className={`pulsing-icon ${hasFault && flashing ? 'flashing' : ''}`} 
                sx={{
                    color: hasFault ? "orange" : "green", 
                    fontSize: "0.5em", // Smaller size
                    marginRight: "4px", 
                }} 
                />
                <Typography variant="body2" sx={{ fontSize: '0.8em', color: 'grey' }}>
                {hasFault ? "Fault Detected" : "Live"}
                </Typography>
            </Box>
        </Box>
        <Typography variant="h3" sx={{ fontSize: '1.8em', marginLeft: 1 }}>
          {actualFlowRate} L/Hr
        </Typography>
      </Box>
      <Collapse in={showPlot} timeout="auto" unmountOnExit>
        <Box mt={2} style={{ height: '300px' }}>
          <Line ref={chartRef} data={chartData} options={chartOptions} />
        </Box>
      </Collapse>
      <Box mt={1} className={`collapsible-section ${showPlot ? 'hidden' : ''}`}>
        <Grid container spacing={1}>
          <Grid item xs={6} textAlign="left">
            <Typography variant="body1" sx={{ fontSize: '1em' }}>Tank Level:</Typography>
          </Grid>
          <Grid item xs={6} textAlign="right">
            <Typography variant="body1" sx={{ fontSize: '1em' }}>{tankLevel} %</Typography>
          </Grid>
          {!showPlot && (
            <>
              <Grid item xs={6} textAlign="left">
                <Typography variant="body1" sx={{ fontSize: '1em' }}>Target Flow Rate:</Typography>
              </Grid>
              <Grid item xs={6} textAlign="right">
                <Typography variant="body1" sx={{ fontSize: '1em' }}>{targetFlow} L/Hr</Typography>
              </Grid>
              <Grid item xs={6} textAlign="left">
                <Typography variant="body1" sx={{ fontSize: '1em' }}>Pressure Delta:</Typography>
              </Grid>
              <Grid item xs={6} textAlign="right">
                <Typography variant="body1" sx={{ fontSize: '1em' }}>{pressureDelta} Bar</Typography>
              </Grid>
              <Grid item xs={6} textAlign="left">
                <Typography variant="body1" sx={{ fontSize: '1em' }}>Strokes/min:</Typography>
              </Grid>
              <Grid item xs={6} textAlign="right">
                <Typography variant="body1" sx={{ fontSize: '1em' }}>{strokesPerMin}</Typography>
              </Grid>
            </>
          )}
        </Grid>
      </Box>
      <Box mt={2} textAlign="center">
        {hasFault && (
          <Button onClick={() => setShowFaults((prev) => !prev)} endIcon={showFaults ? <ExpandLess /> : <ExpandMore />}> 
            {showFaults ? 'Hide Faults' : 'Show Faults'}
          </Button>
        )}
        <Button onClick={() => setShowPlot((prev) => !prev)} sx={{ marginLeft: 1 }}> 
          {showPlot ? 'Hide Plot' : 'Show Plot'}
        </Button>
        <Collapse in={showFaults} timeout="auto" unmountOnExit>
          <Box mt={1}>
            <Typography variant="body2" sx={{ fontSize: '1em' }} color="error">
              Fault detected: Please check the system for issues.
            </Typography>
          </Box>
        </Collapse>
      </Box>
    </Paper>
  );
};

export default TitleBar;
