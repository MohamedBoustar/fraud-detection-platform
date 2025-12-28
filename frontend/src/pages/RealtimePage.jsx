/**
 * RealtimePage - Page principale pour le dashboard temps réel
 */

import React from 'react';
import Navbar from '../components/layout/Navbar';
import RealtimeDashboard from '../components/realtime/RealtimeDashboard';

const RealtimePage = () => {
  return (
    <div className="realtime-page">
      <Navbar />
      <main className="page-content">
        <RealtimeDashboard />
      </main>
    </div>
  );
};

export default RealtimePage;
