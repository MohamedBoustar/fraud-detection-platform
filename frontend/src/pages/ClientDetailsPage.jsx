/**
 * Page ClientDetailsPage - Détails d'un client spécifique
 */
import React, { useState, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';
import ClientProfile from '../components/client/ClientProfile';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

const ClientDetailsPage = () => {
  const [clientData, setClientData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedClient = localStorage.getItem('selectedClient');
    
    if (storedClient) {
      try {
        const parsedClient = JSON.parse(storedClient);
        setClientData(parsedClient);
        localStorage.removeItem('selectedClient');
      } catch (error) {
        console.error('Erreur parsing client data:', error);
      }
    }
    
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <LoadingSpinner fullScreen message="Chargement du profil client..." />
      </div>
    );
  }

  if (!clientData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <ErrorMessage
            type="warning"
            title="Client introuvable"
            message="Aucune donnée de client disponible. Retournez à l'analyse batch."
          />
          <div className="mt-6 text-center">
            <a
              href="/batch"
              className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Retour à l'Analyse Batch
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Bouton retour */}
        <div className="mb-6">
          <a
            href="/batch"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Retour aux résultats
          </a>
        </div>

        {/* Profil Client */}
        <ClientProfile 
          client={clientData} 
          features={clientData.features}
        />
      </div>
    </div>
  );
};

export default ClientDetailsPage;
