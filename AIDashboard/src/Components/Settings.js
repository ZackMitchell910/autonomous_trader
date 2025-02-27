// frontend/src/components/Settings.js
import { useState } from 'react';
import axios from 'axios';

const Settings = ({ user }) => {
    const [strategy, setStrategy] = useState('basic');
    const [risk, setRisk] = useState('medium');

    const saveSettings = async () => {
        await axios.post('/api/set_parameters', { strategy, risk }, {
            headers: { Authorization: `Bearer ${user.token}` }
        });
    };

    return (
        <div>
            <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
                <option value="basic">Basic</option>
                {user.tier === 3 && (
                    <>
                        <option value="arbitrage">Arbitrage</option>
                        <option value="market_making">Market Making</option>
                    </>
                )}
            </select>
            <select value={risk} onChange={(e) => setRisk(e.target.value)}>
                <option value="low">Low Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="high">High Risk</option>
            </select>
            <button onClick={saveSettings}>Save</button>
        </div>
    );
};