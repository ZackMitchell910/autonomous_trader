// src/components/Sidebar.js
import React from 'react';

const Sidebar = ({ setSection }) => (
  <div className="sidebar">
    <ul>
      <li onClick={() => setSection('Home')}>Home</li>
      <li onClick={() => setSection('Signals')}>Signals</li>
      <li onClick={() => setSection('Market Overview')}>Market Overview</li>
      <li onClick={() => setSection('Settings')}>Settings</li>
    </ul>
  </div>
);

export default Sidebar;