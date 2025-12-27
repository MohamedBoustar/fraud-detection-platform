/**
 * RealtimePage - Page principale pour le dashboard temps réel
 */

import React from 'react';
import Navbar from '../components/layout/Navbar';
import RealtimeDashboard from '../components/realtime/RealtimeDashboard';
import AlertNotification from '../components/realtime/AlertNotification';

const RealtimePage = () => {
  return (
    <div className="realtime-page">
      <Navbar />
      <AlertNotification />
      <main className="page-content">
        <RealtimeDashboard />
      </main>
    </div>
  );
};

export default RealtimePage;
