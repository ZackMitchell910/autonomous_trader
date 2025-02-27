// frontend/src/components/Dashboard.js
import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

const Dashboard = ({ user }) => {
    const [trades, setTrades] = useState([]);

    useEffect(() => {
        const ws = new WebSocket(`ws://localhost:8000/ws?token=${user.token}`);
        ws.onmessage = (event) => {
            const trade = JSON.parse(event.data);
            setTrades((prev) => [...prev, trade]);
        };
        return () => ws.close();
    }, []);

    const chartData = {
        labels: trades.map(t => t.timestamp),
        datasets: [{ label: 'Profit', data: trades.map(t => t.profit) }]
    };

    return <Line data={chartData} />;
};