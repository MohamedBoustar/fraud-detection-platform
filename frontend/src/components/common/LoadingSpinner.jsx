/**
 * Composant LoadingSpinner - Indicateur de chargement
 */
import React from 'react';

const LoadingSpinner = ({ 
  size = 'md', 
  message = 'Chargement...', 
  fullScreen = false 
}) => {
  // Tailles du spinner
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };

  const spinnerSize = sizes[size] || sizes.md;

  // Conteneur
  const containerClass = fullScreen
    ? 'fixed inset-0 flex flex-col items-center justify-center bg-white bg-opacity-90 z-50'
    : 'flex flex-col items-center justify-center p-8';

  return (
    <div className={containerClass}>
      {/* Spinner animé */}
      <div
        className={`${spinnerSize} border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin`}
        role="status"
        aria-label="Chargement"
      />
      
      {/* Message optionnel */}
      {message && (
        <p className="mt-4 text-gray-600 text-center font-medium">
          {message}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;