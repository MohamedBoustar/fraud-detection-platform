/**
 * RealtimeChart - Graphique temps réel avec Recharts
 * Affiche l'historique des scores de fraude
 */

import React, { useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import useRealtimeData from '../../hooks/useRealtimeData';

const RealtimeChart = ({ type = 'line', limit = 30 }) => {
  const realtime = useRealtimeData();

  // Préparer les données pour le graphique
  const chartData = useMemo(() => {
    return realtime.predictions
      .slice(0, limit)
      .reverse()
      .map((pred, idx) => ({
        time: idx,
        meter: pred.meter_id.slice(-4), // Derniers 4 caractères
        score: (pred.fraud_probability * 100).toFixed(1),
        consumption: pred.consumption_kw?.toFixed(1) || 0,
        risk: pred.risk_level,
        isFraud: pred.is_fraud,
      }));
  }, [realtime.predictions, limit]);

  if (realtime.predictions.length === 0) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
        En attente des données...
      </div>
    );
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          style={{
            background: 'white',
            padding: '8px 12px',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            fontSize: '12px',
          }}
        >
          <p style={{ margin: '0', fontWeight: 'bold' }}>
            {data.meter}
          </p>
          <p style={{ margin: '4px 0 0 0', color: '#ef4444' }}>
            Score: {data.score}%
          </p>
          <p style={{ margin: '2px 0 0 0', color: '#6b7280' }}>
            Consommation: {data.consumption}kW
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height: '300px', marginBottom: '20px' }}>
      {type === 'line' ? (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="meter"
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#ef4444"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name="Score fraude (%)"
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="meter"
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              domain={[0, 100]}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar
              dataKey="score"
              fill="#3b82f6"
              name="Score fraude (%)"
              radius={[8, 8, 0, 0]}
            />
            <Bar
              dataKey="consumption"
              fill="#8b5cf6"
              name="Consommation (kW)"
              radius={[8, 8, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default RealtimeChart;
