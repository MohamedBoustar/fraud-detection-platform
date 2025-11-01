/**
 * Page BatchPage - Page principale d'analyse batch
 */
import React, { useState } from 'react';
import Navbar from '../components/layout/Navbar';
import FileUploader from '../components/batch/FileUploader';
import BatchResults from '../components/batch/BatchResults';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { predictBatch } from '../services/api';

const BatchPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Fonction d'upload et analyse
  const handleUpload = async (file, threshold) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      console.log(`📤 Upload fichier: ${file.name} avec seuil: ${threshold}`);
      
      // Appel API
      const data = await predictBatch(file, threshold);
      
      console.log('✅ Résultats reçus:', data);
      setResults(data);
      
    } catch (err) {
      console.error('❌ Erreur:', err);
      
      const errorMessage = err.response?.data?.detail 
        || err.message 
        || "Une erreur est survenue lors de l'analyse";
      
      setError(errorMessage);
      
    } finally {
      setIsLoading(false);
    }
  };

  // Fonction de retry
  const handleRetry = () => {
    setError(null);
    setResults(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Titre de la page */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📤 Analyse Batch
          </h1>
          <p className="text-gray-600">
            Uploadez un fichier CSV pour analyser plusieurs clients en une fois
          </p>
        </div>

        {/* FileUploader */}
        <FileUploader onUpload={handleUpload} isLoading={isLoading} />

        {/* Loading */}
        {isLoading && (
          <div className="mt-6">
            <LoadingSpinner 
              size="lg" 
              message="Analyse en cours... Cela peut prendre quelques instants."
            />
          </div>
        )}

        {/* Erreur */}
        {error && !isLoading && (
          <ErrorMessage
            type="error"
            title="Erreur lors de l'analyse"
            message={error}
            onRetry={handleRetry}
          />
        )}

        {/* Résultats */}
        {results && !isLoading && !error && (
          <BatchResults data={results} />
        )}
      </div>
    </div>
  );
};

export default BatchPage;