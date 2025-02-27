// src/components/WalletConnector.js
import React, { useState } from 'react';

const WalletConnector = ({ setPublicKey }) => {
  const [isConnected, setIsConnected] = useState(false);

  const connectWallet = async () => {
    if (window.solana && window.solana.isPhantom) {
      try {
        const response = await window.solana.connect();
        setPublicKey(response.publicKey.toString());
        setIsConnected(true);
      } catch (err) {
        console.error('Connection error:', err);
        alert('Failed to connect wallet');
      }
    } else {
      alert('Please install Phantom wallet');
    }
  };

  return (
    <button className="connect-btn" onClick={connectWallet}>
      {isConnected ? 'Connected' : 'Connect Phantom Wallet'}
    </button>
  );
};

export default WalletConnector;