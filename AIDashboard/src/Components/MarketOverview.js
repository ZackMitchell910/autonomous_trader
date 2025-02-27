// src/components/MarketOverview.js
import React from 'react';
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
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const MarketOverview = ({ tier }) => {
  const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [
      {
        label: 'SOL Price',
        data: [100, 120, 110, 130, 140],
        borderColor: 'rgba(75,192,192,1)',
        fill: false,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { position: 'top' } },
  };

  return (
    <div className="market-overview">
      <h2>Market Overview</h2>
      <Line data={data} options={options} />
      {tier === 'Basic' && (
        <p>Upgrade to Advanced or Premium for more metrics!</p>
      )}
      {/* Add more charts for Advanced/Premium tiers */}
    </div>
  );
};

export default MarketOverview;