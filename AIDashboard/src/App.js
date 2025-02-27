// src/App.js
import React, { useState, useEffect } from 'react';
import WalletConnector from './components/WalletConnector';
import TopBar from './components/TopBar';
import Sidebar from './components/Sidebar';
import MainArea from './components/MainArea';
import Footer from './components/Footer';
import { getSparkBalance, determineTier } from './utils/getTier';
import { Connection, PublicKey } from '@solana/web3.js';
import { getMint } from '@solana/spl-token';
import './App.css';

const App = () => {
  const [publicKey, setPublicKey] = useState(null);
  const [sparkBalance, setSparkBalance] = useState(BigInt(0));
  const [tier, setTier] = useState('Basic');
  const [section, setSection] = useState('Home');
  const [decimals, setDecimals] = useState(null);

  // Fetch token decimals once on app load
  useEffect(() => {
    const fetchDecimals = async () => {
      const connection = new Connection('https://api.mainnet-beta.solana.com');
      const mintAddress = new PublicKey('53mTqqc1GFKiLdG9eM282FYFde6muDxqa5mppGEmC8Rm');
      const mintInfo = await getMint(connection, mintAddress);
      setDecimals(mintInfo.decimals);
    };
    fetchDecimals();
  }, []);

  // Fetch balance and determine tier when publicKey or decimals change
  useEffect(() => {
    if (publicKey && decimals !== null) {
      getSparkBalance(publicKey).then((balance) => {
        setSparkBalance(balance);
        const userTier = determineTier(balance, decimals);
        setTier(userTier);
      });
    }
  }, [publicKey, decimals]);

  return (
    <div className="app">
      {!publicKey ? (
        <div className="wallet-connect-container">
          <WalletConnector setPublicKey={setPublicKey} />
        </div>
      ) : (
        <>
          <TopBar publicKey={publicKey} sparkBalance={sparkBalance} tier={tier} decimals={decimals} />
          <div className="dashboard">
            <Sidebar setSection={setSection} />
            <MainArea section={section} tier={tier} />
          </div>
          <Footer />
        </>
      )}
    </div>
  );
};

export default App;