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
      {tier === 'Tier 1' && <p>Upgrade to Tier 2 or Tier 3 for more metrics.</p>}
      {(tier === 'Tier 2' || tier === 'Tier 3') && <p>Advanced charts available for your tier.</p>}
    </div>
  );
};

export default MarketOverview;