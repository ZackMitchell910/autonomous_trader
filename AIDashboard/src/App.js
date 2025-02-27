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
  const [sparkBalanceSmallestUnit, setSparkBalanceSmallestUnit] = useState(BigInt(0));
  const [sparkBalance, setSparkBalance] = useState(0);
  const [tier, setTier] = useState('None');
  const [section, setSection] = useState('Home');
  const [decimals, setDecimals] = useState(null);

  useEffect(() => {
    const fetchDecimals = async () => {
      try {
        const connection = new Connection('https://api.mainnet-beta.solana.com');
        const mintAddress = new PublicKey('53mTqqc1GFKiLdG9eM282FYFde6muDxqa5mppGEmC8Rm');
        const mintInfo = await getMint(connection, mintAddress);
        setDecimals(mintInfo.decimals);
      } catch (err) {
        console.error('Error fetching decimals:', err);
        setDecimals(9); // Fallback to common decimal value
      }
    };
    fetchDecimals();
  }, []);

  useEffect(() => {
    if (publicKey && decimals !== null) {
      getSparkBalance(publicKey).then((balance) => {
        setSparkBalanceSmallestUnit(balance);
        const wholeTokens = balance / (BigInt(10) ** BigInt(decimals));
        setSparkBalance(wholeTokens.toString());
        setTier(determineTier(wholeTokens));
      }).catch(err => console.error('Balance fetch error:', err));
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
          <TopBar publicKey={publicKey} sparkBalance={sparkBalance} tier={tier} />
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