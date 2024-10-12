import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';
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

const TimeIntervalChart = () => {
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

  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const fetchData = async () => {
    if (!startDate || !endDate) {
      alert("Please select both start and end dates.");
      return;
    }

    const startTimestamp = new Date(startDate).getTime();
    const endTimestamp = new Date(endDate).getTime();

    const url = `https://rypkpzb851.execute-api.us-east-1.amazonaws.com/1/data?start_timestamp=${startTimestamp}&end_timestamp=${endTimestamp}`;

    try {
      const response = await axios.get(url);
      const fetchedData = response.data;
      console.log(response.data)

      const newLabels = fetchedData.map(item => new Date(item.timestamp));
      const newTemperatureData = fetchedData.map(item => parseFloat(item.temp));
      const newHumidityData = fetchedData.map(item => parseFloat(item.hum));

      setData({
        labels: newLabels,
        datasets: [
          {
            ...data.datasets[0],
            data: newTemperatureData,
          },
          {
            ...data.datasets[1],
            data: newHumidityData,
          },
        ],
      });
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

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
          unit: 'minute',
          stepSize: 20,
        },
      },
      y: {
        beginAtZero: true,
      },
    },
  };
  

  return (
    <div>
      <h2>Chart between Two Time Intervals</h2>
      <div>
        <label>
          Start Date:
          <input
            type="datetime-local"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </label>
        <label>
          End Date:
          <input
            type="datetime-local"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </label>
        <button onClick={fetchData}>Fetch Data</button>
      </div>
      <Line data={data} options={options} />
    </div>
  );
};

export default TimeIntervalChart;
