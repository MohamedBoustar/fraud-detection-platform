/**
 * Composant RiskBadge - Badge de niveau de risque
 */
import React from 'react';
import { formatRiskLevel } from '../../utils/formatters';

const RiskBadge = ({ 
  riskLevel, 
  probability = null, 
  size = 'md',
  showIcon = true 
}) => {
  const { text, color, icon } = formatRiskLevel(riskLevel);

  // Tailles
  const sizes = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2',
  };

  const badgeSize = sizes[size] || sizes.md;

  return (
    <div className="inline-flex items-center space-x-2">
      {/* Badge principal */}
      <span
        className={`${badgeSize} rounded-full font-semibold inline-flex items-center`}
        style={{
          backgroundColor: `${color}15`,
          color: color,
          border: `2px solid ${color}`,
        }}
      >
        {showIcon && <span className="mr-1">{icon}</span>}
        {text}
      </span>

      {/* Probabilité optionnelle */}
      {probability !== null && (
        <span className="text-sm text-gray-600 font-medium">
          ({(probability * 100).toFixed(1)}%)
        </span>
      )}
    </div>
  );
};

export default RiskBadge;