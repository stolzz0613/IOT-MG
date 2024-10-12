import { useEffect, useRef, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const RealTimeChart = () => {
  const [data, setData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Temperature',
        data: [],
        borderColor: 'rgba(255, 99, 132, 1)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        fill: true,
      },
      {
        label: 'Humidity',
        data: [],
        borderColor: 'rgba(54, 162, 235, 1)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        fill: true,
      },
    ],
  });

  const ws = useRef(null);

  useEffect(() => {
    const wsUrl = 'wss://re4xscfbzl.execute-api.us-east-1.amazonaws.com/production';
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket connection opened');
    };

    ws.current.onmessage = (event) => {

      const message = JSON.parse(event.data);
      const { temp, hum, timestamp } = message;
      console.log(message)
      setData((prevData) => {
        const newLabels = [...prevData.labels, new Date(timestamp)];
        const newTemperatureData = [...prevData.datasets[0].data, parseFloat(temp)];
        const newHumidityData = [...prevData.datasets[1].data, parseFloat(hum)];
        console.log(newLabels)

        if (newLabels.length > 10) {
          newLabels.shift();
          newTemperatureData.shift();
          newHumidityData.shift();
        }

        return {
          labels: newLabels,
          datasets: [
            {
              ...prevData.datasets[0],
              data: newTemperatureData,
            },
            {
              ...prevData.datasets[1],
              data: newHumidityData,
            },
          ],
        };
      });
    };

    ws.current.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'second',
        },
      },
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div>
      <h2>Real-Time Temperature and Humidity</h2>
      <Line data={data} options={options} />
    </div>
  );
};

export default RealTimeChart;
