// pages/index.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import Head from "next/head";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { motion } from "framer-motion";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// ----- Spinner Component -----
const Spinner = () => (
  <div className="flex justify-center items-center py-4">
    <div className="w-12 h-12 border-4 border-blue-500 border-dashed rounded-full animate-spin"></div>
  </div>
);

// ----- Navigation Bar Component -----
const NavBar = () => (
  <header className="sticky top-0 z-50 bg-gradient-to-r from-blue-900 to-purple-900 shadow-lg">
    <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-16">
      <div className="text-white font-bold text-2xl">SPARK AI Trading</div>
      <div className="space-x-6">
        {["login", "exchange", "analytics", "positions", "livechart"].map(
          (section) => (
            <a
              key={section}
              href={`#${section}`}
              className="text-gray-200 hover:text-white transition-colors duration-300"
            >
              {section.charAt(0).toUpperCase() + section.slice(1)}
            </a>
          )
        )}
      </div>
    </nav>
  </header>
);

// ----- Login Section Component -----
const LoginSection = ({ wallet, loginWithPhantom, token, sparkBalance, eligible }) => (
  <section id="login" className="mb-12 flex flex-col items-center">
    <motion.div
      className="w-full max-w-xl text-center"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {!wallet ? (
        <button
          onClick={loginWithPhantom}
          className="bg-gray-800 hover:bg-gray-700 transition-colors duration-300 px-8 py-4 rounded-md text-xl focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-md"
        >
          Login with Phantom Wallet
        </button>
      ) : (
        <p className="mb-4">
          Connected:{" "}
          <span className="text-green-400">{wallet.publicKey.toString()}</span>
        </p>
      )}
      {token && (
        <p className="mb-2">
          SPARK Token Balance:{" "}
          <span className="font-bold">{sparkBalance}</span>{" "}
          {eligible ? (
            <span className="text-green-500">✅ Access Granted</span>
          ) : (
            <span className="text-red-500">❌ Insufficient Balance</span>
          )}
        </p>
      )}
    </motion.div>
  </section>
);

// ----- Exchange Section Component -----
const ExchangeSection = ({ selectedExchange, handleExchangeChange, connectExchange }) => (
  <section id="exchange" className="mb-12">
    <motion.div
      className="max-w-xl mx-auto text-center"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
    >
      <h2 className="text-3xl font-semibold mb-6">Connect Exchange</h2>
      <div className="flex flex-col items-center">
        <select
          value={selectedExchange}
          onChange={handleExchangeChange}
          className="bg-gray-800 border border-gray-700 rounded-md px-4 py-2 mb-4 text-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="Binance">Binance</option>
          <option value="Coinbase">Coinbase</option>
          <option value="Kraken">Kraken</option>
          <option value="FTX">FTX</option>
          <option value="Other">Other</option>
        </select>
        <button
          onClick={connectExchange}
          className="bg-blue-600 hover:bg-blue-500 transition-colors duration-300 px-8 py-4 rounded-md text-xl focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-md"
        >
          Connect to {selectedExchange}
        </button>
      </div>
    </motion.div>
  </section>
);

// ----- Analytics Section Component -----
const AnalyticsSection = ({ performanceData, chartOptions }) => (
  <section id="analytics" className="mb-12">
    <motion.div
      className="max-w-4xl mx-auto bg-gray-900 p-6 rounded-lg shadow-xl"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
    >
      <h2 className="text-3xl font-semibold text-center mb-6">Trading Performance Analytics</h2>
      <div style={{ height: "400px" }}>
        {performanceData ? (
          <Line data={performanceData} options={chartOptions} />
        ) : (
          <Spinner />
        )}
      </div>
    </motion.div>
  </section>
);

// ----- Trade Summary Section Component -----
const TradeSummarySection = ({ tradeSummary }) => (
  <section id="positions" className="mb-12">
    <motion.div
      className="max-w-4xl mx-auto bg-gray-900 p-6 rounded-lg shadow-xl"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
    >
      <h2 className="text-3xl font-semibold text-center mb-6">
        Current Positions & Trade Summary
      </h2>
      <div className="mb-4">
        <h3 className="text-xl font-bold">Current Positions:</h3>
        {tradeSummary.positions && tradeSummary.positions.length > 0 ? (
          <ul className="mt-2 space-y-2">
            {tradeSummary.positions.map((pos, idx) => (
              <li key={idx} className="text-lg">
                {pos.symbol}: {pos.amount}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-400">No positions available.</p>
        )}
      </div>
      <div className="mb-2 text-lg">
        <strong>Profit/Loss:</strong> ${tradeSummary.pnl.toFixed(2)}
      </div>
      <div className="mb-2 text-lg">
        <strong>Balance:</strong> ${tradeSummary.balance.toFixed(2)}
      </div>
      <div className="text-lg">
        <strong>Number of Trades:</strong> {tradeSummary.tradeCount}
      </div>
    </motion.div>
  </section>
);

// ----- AI Trading Controls Section Component -----
const AIControlsSection = ({ eligible, startAI, stopAI }) => (
  <section className="mb-12 flex flex-col items-center">
    <motion.div
      className="flex space-x-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <button
        onClick={startAI}
        disabled={!eligible}
        className={`px-8 py-4 rounded-md text-xl transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-green-500 shadow-md ${
          eligible
            ? "bg-green-600 hover:bg-green-500 cursor-pointer"
            : "bg-gray-600 cursor-not-allowed"
        }`}
      >
        Start AI Trading
      </button>
      <button
        onClick={stopAI}
        className="bg-red-600 hover:bg-red-500 transition-colors duration-300 px-8 py-4 rounded-md text-xl focus:outline-none focus:ring-2 focus:ring-red-500 shadow-md"
      >
        Stop AI Trading
      </button>
    </motion.div>
  </section>
);

// ----- Live Chart Section Component -----
const LiveChartSection = () => (
  <section id="livechart" className="mb-12">
    <motion.div
      className="max-w-4xl mx-auto"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
    >
      <h2 className="text-3xl font-semibold text-center mb-6">
        SPARK Token Live Chart
      </h2>
      <iframe
        src="https://dexscreener.com/solana/53mTqqc1GFKiLdG9eM282FYFde6muDxqa5mppGEmC8Rm"
        width="100%"
        height="400px"
        className="rounded-lg border-0 shadow-xl"
      ></iframe>
    </motion.div>
  </section>
);

// ----- Footer Component -----
const Footer = () => (
  <footer className="text-center mt-10 text-gray-500 py-4 border-t border-gray-800">
    <p>&copy; {new Date().getFullYear()} SPARK AI Trading. All rights reserved.</p>
  </footer>
);

// ----- Main HomePage Component -----
export default function HomePage() {
  const [wallet, setWallet] = useState(null);
  const [token, setToken] = useState(null);
  const [eligible, setEligible] = useState(false);
  const [sparkBalance, setSparkBalance] = useState(0);
  const [performanceData, setPerformanceData] = useState(null);
  const [selectedExchange, setSelectedExchange] = useState("Binance");
  const [tradeSummary, setTradeSummary] = useState({
    positions: [],
    pnl: 0,
    balance: 0,
    tradeCount: 0,
  });

  // Use environment variable for backend URL; ensure NEXT_PUBLIC_BACKEND_URL is set.
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://YOUR_BACKEND_IP:8000";

  // ----- Toast Notification Helpers -----
  const notifyError = (message) =>
    toast.error(message, { position: toast.POSITION.TOP_RIGHT });
  const notifySuccess = (message) =>
    toast.success(message, { position: toast.POSITION.TOP_RIGHT });

  useEffect(() => {
    if (window.solana && window.solana.isPhantom) {
      window.solana.on("connect", () => {
        setWallet(window.solana);
      });
    }
  }, []);

  const loginWithPhantom = async () => {
    if (!window.solana) {
      notifyError("Phantom Wallet not installed!");
      return;
    }
    try {
      const provider = window.solana;
      await provider.connect();
      /*eslint-disable-next-line @typescript-eslint/no-unused-vars*/
      const walletAddress = provider.publicKey.toString();
      console.log(walletAddress); 

      // Authenticate with backend (update as needed)
      const authResponse = await axios.post(`${backendUrl}/auth/phantom`, {
        address: walletAddress,
      });

      setToken(authResponse.data.token);
      checkSparkBalance(walletAddress);
      fetchPerformanceData(walletAddress);
      fetchTradeSummary(walletAddress);
      notifySuccess("Wallet connected successfully");
    } catch (error) {
      console.error("Login failed:", error);
      notifyError("Login failed, please try again.");
    }
  };

  const checkSparkBalance = async (walletAddress) => {
    try {
      const response = await axios.get(
        `${backendUrl}/check-spark-balance/${walletAddress}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSparkBalance(response.data.balance);
      setEligible(response.data.eligible);
    } catch (error) {
      console.error("Failed to fetch balance:", error);
      notifyError("Failed to fetch token balance.");
    }
  };

  const fetchPerformanceData = async (walletAddress) => {
    try {
      const response = await axios.get(
        `${backendUrl}/performance/${walletAddress}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPerformanceData(response.data);
    } catch (error) {
      console.error("Failed to fetch performance data:", error);
      notifyError("Failed to fetch performance data.");
    }
  };

  const fetchTradeSummary = async (walletAddress) => {
    try {
      const response = await axios.get(
        `${backendUrl}/trade-summary/${walletAddress}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTradeSummary(response.data);
    } catch (error) {
      console.error("Failed to fetch trade summary:", error);
      notifyError("Failed to fetch trade summary.");
    }
  };

  const startAI = async () => {
    if (!eligible) {
      notifyError("You need at least 1,000,000 SPARK tokens to use the AI Trader.");
      return;
    }
    try {
      await axios.post(
        `${backendUrl}/ai/start`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      notifySuccess("AI Trading Started");
    } catch (error) {
      console.error("Error starting AI trading:", error);
      notifyError("Error starting AI trading.");
    }
  };

  const stopAI = async () => {
    try {
      await axios.post(
        `${backendUrl}/ai/stop`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      notifySuccess("AI Trading Stopped");
    } catch (error) {
      console.error("Error stopping AI trading:", error);
      notifyError("Error stopping AI trading.");
    }
  };

  const handleExchangeChange = (e) => {
    setSelectedExchange(e.target.value);
  };

  const connectExchange = async () => {
    try {
      const response = await axios.post(
        `${backendUrl}/exchange/connect`,
        {
          exchange: selectedExchange,
          walletAddress: wallet.publicKey.toString(),
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      notifySuccess(`Connected to ${selectedExchange}: ${response.data.status}`);
    } catch (error) {
      console.error("Exchange connection failed:", error);
      notifyError(`Failed to connect to ${selectedExchange}`);
    }
  };

  // ----- Chart Options for Performance Analytics -----
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: "top" },
      title: { display: true, text: "AI Trading Performance" },
      tooltip: { enabled: true },
    },
  };

  return (
    <div className="min-h-screen bg-black text-white font-sans">
      <Head>
        <title>SPARK AI Trading</title>
        <meta name="description" content="Exclusive AI Trading platform for SPARK token holders" />
      </Head>
      <NavBar />
      <main className="px-4 py-8">
        <motion.header
          className="text-center mb-12"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-5xl font-extrabold">SPARK AI Trading</h1>
          <p className="mt-2 text-xl text-gray-400">
            Exclusive access for users holding at least 1,000,000 SPARK tokens
          </p>
        </motion.header>
        <LoginSection
          wallet={wallet}
          loginWithPhantom={loginWithPhantom}
          token={token}
          sparkBalance={sparkBalance}
          eligible={eligible}
        />
        <ExchangeSection
          selectedExchange={selectedExchange}
          handleExchangeChange={handleExchangeChange}
          connectExchange={connectExchange}
        />
        <AnalyticsSection performanceData={performanceData} chartOptions={chartOptions} />
        <TradeSummarySection tradeSummary={tradeSummary} />
        <AIControlsSection eligible={eligible} startAI={startAI} stopAI={stopAI} />
        <LiveChartSection />
      </main>
      <Footer />
      <ToastContainer />
    </div>
  );
}
