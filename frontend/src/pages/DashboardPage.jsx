/**
 * DashboardPage - Dashboard principal avec statistiques globales
 */
import React, { useState, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';

const DashboardPage = () => {
  const [stats, setStats] = useState(null);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Récupérer les batches
      const batchRes = await fetch('http://localhost:8000/api/predictions/batches');
      const batchData = await batchRes.json();
      setBatches(batchData.batches || []);

      // Calculer les statistiques
      const totalBatches = batchData.batches?.length || 0;
      const totalClients = batchData.batches?.reduce((sum, b) => sum + (b.total_clients || 0), 0) || 0;
      const totalFrauds = batchData.batches?.reduce((sum, b) => sum + (b.fraud_detected || 0), 0) || 0;
      const avgFraudRate = totalClients > 0 ? (totalFrauds / totalClients * 100) : 0;

      setStats({
        totalBatches,
        totalClients,
        totalFrauds,
        totalNormal: totalClients - totalFrauds,
        avgFraudRate: avgFraudRate.toFixed(1)
      });

    } catch (error) {
      console.error('Erreur chargement données:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement du dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Vue d'ensemble des analyses de fraude</p>
        </div>

        {/* Statistiques principales */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Analyses */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Analyses</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats?.totalBatches || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Total Clients */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Total Clients</p>
                <p className="text-3xl font-bold text-gray-900 mt-1">{stats?.totalClients || 0}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Fraudeurs Détectés */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Fraudeurs Détectés</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{stats?.totalFrauds || 0}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Taux de Fraude */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Taux de Fraude</p>
                <p className="text-3xl font-bold text-yellow-600 mt-1">{stats?.avgFraudRate || 0}%</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Répartition Fraud/Normal */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Carte Répartition */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Répartition des Clients</h2>
            
            <div className="flex items-center justify-center space-x-8">
              {/* Normal */}
              <div className="text-center">
                <div className="w-24 h-24 rounded-full bg-green-100 flex items-center justify-center mb-2">
                  <span className="text-2xl font-bold text-green-600">{stats?.totalNormal || 0}</span>
                </div>
                <p className="text-sm font-medium text-gray-600">Normaux</p>
              </div>

              {/* Fraudeurs */}
              <div className="text-center">
                <div className="w-24 h-24 rounded-full bg-red-100 flex items-center justify-center mb-2">
                  <span className="text-2xl font-bold text-red-600">{stats?.totalFrauds || 0}</span>
                </div>
                <p className="text-sm font-medium text-gray-600">Fraudeurs</p>
              </div>
            </div>

            {/* Barre de progression */}
            <div className="mt-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Normal ({stats?.totalClients > 0 ? ((stats?.totalNormal / stats?.totalClients) * 100).toFixed(1) : 0}%)</span>
                <span>Fraude ({stats?.avgFraudRate || 0}%)</span>
              </div>
              <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 rounded-full"
                  style={{ width: `${stats?.totalClients > 0 ? ((stats?.totalNormal / stats?.totalClients) * 100) : 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Actions Rapides */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions Rapides</h2>
            
            <div className="space-y-3">
              <a 
                href="/batch"
                className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mr-4">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Nouvelle Analyse</p>
                  <p className="text-sm text-gray-600">Uploader un fichier CSV</p>
                </div>
              </a>

              <a 
                href="/realtime"
                className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
              >
                <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center mr-4">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Temps Réel</p>
                  <p className="text-sm text-gray-600">Surveillance IoT en direct</p>
                </div>
              </a>

              <a 
                href="/history"
                className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
              >
                <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center mr-4">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Historique</p>
                  <p className="text-sm text-gray-600">Voir les analyses passées</p>
                </div>
              </a>
            </div>
          </div>
        </div>

        {/* Dernières Analyses */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Dernières Analyses</h2>
          
          {batches.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">Aucune analyse effectuée</p>
              <a href="/batch" className="text-blue-600 hover:underline mt-2 inline-block">
                Faire une première analyse
              </a>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Fichier</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Date</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">Clients</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">Fraudeurs</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">Taux</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-gray-500">Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {batches.slice(0, 5).map((batch, idx) => (
                    <tr key={batch.id || idx} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <span className="font-medium text-gray-900">{batch.filename}</span>
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {new Date(batch.upload_timestamp).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="py-3 px-4 text-center text-gray-900">{batch.total_clients}</td>
                      <td className="py-3 px-4 text-center">
                        <span className="text-red-600 font-semibold">{batch.fraud_detected}</span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="text-yellow-600 font-semibold">
                          {batch.fraud_percentage?.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          batch.status === 'completed' 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {batch.status === 'completed' ? 'Terminé' : 'En cours'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
