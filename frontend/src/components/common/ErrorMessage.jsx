/**
 * Composant ErrorMessage - Affichage d'erreurs
 */
import React from 'react';

const ErrorMessage = ({ 
  message, 
  title = 'Erreur', 
  onRetry = null,
  type = 'error' // 'error', 'warning', 'info'
}) => {
  // Couleurs selon le type
  const styles = {
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      icon: '❌',
      iconColor: 'text-red-600',
      textColor: 'text-red-800',
      titleColor: 'text-red-900',
      buttonBg: 'bg-red-600 hover:bg-red-700',
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      icon: '⚠️',
      iconColor: 'text-yellow-600',
      textColor: 'text-yellow-800',
      titleColor: 'text-yellow-900',
      buttonBg: 'bg-yellow-600 hover:bg-yellow-700',
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: 'ℹ️',
      iconColor: 'text-blue-600',
      textColor: 'text-blue-800',
      titleColor: 'text-blue-900',
      buttonBg: 'bg-blue-600 hover:bg-blue-700',
    },
  };

  const style = styles[type] || styles.error;

  return (
    <div 
      className={`${style.bg} border ${style.border} rounded-lg p-6 my-4`}
      role="alert"
    >
      <div className="flex items-start">
        {/* Icône */}
        <div className={`text-3xl ${style.iconColor} mr-4`}>
          {style.icon}
        </div>

        {/* Contenu */}
        <div className="flex-1">
          {/* Titre */}
          <h3 className={`text-lg font-semibold ${style.titleColor} mb-2`}>
            {title}
          </h3>

          {/* Message */}
          <p className={`${style.textColor} mb-4`}>
            {message}
          </p>

          {/* Bouton Retry optionnel */}
          {onRetry && (
            <button
              onClick={onRetry}
              className={`${style.buttonBg} text-white px-4 py-2 rounded-md font-medium transition-colors`}
            >
              🔄 Réessayer
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;