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
    // Récupère les données depuis localStorage
    const storedClient = localStorage.getItem('selectedClient');
    
    if (storedClient) {
      try {
        const parsedClient = JSON.parse(storedClient);
        setClientData(parsedClient);
        
        // Nettoie localStorage après utilisation
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
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
            >
              ← Retour à l'Analyse Batch
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
            className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
          >
            ← Retour aux résultats
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
