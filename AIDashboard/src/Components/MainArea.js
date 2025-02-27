// src/components/MainArea.js
import React from 'react';
import Signals from './Signals';
import MarketOverview from './MarketOverview';

const MainArea = ({ section, tier }) => {
  switch (section) {
    case 'Signals':
      return <Signals tier={tier} />;
    case 'Market Overview':
      return <MarketOverview tier={tier} />;
    case 'Settings':
      return <div>Settings (Tier: {tier}) - Coming Soon!</div>;
    default:
      return <div>Welcome to Spark AI Trader!</div>;
  }
};

export default MainArea;