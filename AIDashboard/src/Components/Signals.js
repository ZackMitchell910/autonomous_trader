import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const Signals = ({ tier }) => {
  const [signals, setSignals] = useState([
    { asset: 'SOL', signal: 'Buy', confidence: '85%' },
    { asset: 'ETH', signal: 'Sell', confidence: '90%' },
    // Add more mock signals as needed
  ]);

  useEffect(() => {
    if (tier === 'Tier 3') {
      const socket = io('http://localhost:3001');
      socket.on('newSignal', (newSignal) => {
        setSignals((prev) => [...prev, newSignal]);
      });
      return () => socket.disconnect();
    }
  }, [tier]);

  const maxSignals = { 'Tier 1': 5, 'Tier 2': 20, 'Tier 3': signals.length };
  const visibleSignals = signals.slice(0, maxSignals[tier] || 5);

  return (
    <div className="signals">
      <h2>Trading Signals</h2>
      {visibleSignals.map((signal, index) => (
        <div key={index} className="signal-card">
          {signal.asset}: {signal.signal} ({signal.confidence})
        </div>
      ))}
      {tier !== 'Tier 3' && <p>Hold more Spark to unlock additional signals.</p>}
    </div>
  );
};

export default Signals;