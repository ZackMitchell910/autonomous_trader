// src/components/TopBar.js
import React from 'react';

const TopBar = ({ publicKey, sparkBalance, tier, decimals }) => {
  const wholeTokens = decimals ? sparkBalance / (BigInt(10) ** BigInt(decimals)) : BigInt(0);
  return (
    <div className="top-bar">
      <div>Spark AI Trader</div>
      <div>Wallet: {publicKey.slice(0, 6)}...{publicKey.slice(-4)}</div>
      <div>Spark: {wholeTokens.toString()}</div>
      <div>Tier: {tier}</div>
      <button onClick={() => window.solana.disconnect()}>Logout</button>
    </div>
  );
};

export default TopBar;