/**
 * Composant BatchResults - Affichage des résultats de prédiction
 */
import React, { useState, useMemo } from 'react';
import RiskBadge from '../common/RiskBadge';
import { formatPredictionLabel, formatPercentage, formatNumber } from '../../utils/formatters';




const BatchResults = ({ data }) => {
  // Fonction pour naviguer vers le détail client
  const handleViewClient = (item) => {
    // Stocke les données du client dans localStorage
    localStorage.setItem('selectedClient', JSON.stringify(item));
    
    // Navigation
    window.location.href = `/client/${item.cons_no || item.index}`;
  };
  
  const [filter, setFilter] = useState('all'); // 'all', 'fraud', 'normal'
  const [sortBy, setSortBy] = useState('probability'); // 'probability', 'cons_no'
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc', 'desc'
  const [searchTerm, setSearchTerm] = useState('');

  // Données filtrées et triées
  const filteredData = useMemo(() => {
    let filtered = [...data.predictions];

    // Filtre par statut
    if (filter === 'fraud') {
      filtered = filtered.filter((item) => item.prediction === 1);
    } else if (filter === 'normal') {
      filtered = filtered.filter((item) => item.prediction === 0);
    }

    // Filtre par recherche (CONS_NO)
    if (searchTerm) {
      filtered = filtered.filter((item) =>
        item.cons_no?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Tri
    filtered.sort((a, b) => {
      let comparison = 0;

      if (sortBy === 'probability') {
        comparison = a.probability - b.probability;
      } else if (sortBy === 'cons_no') {
        comparison = (a.cons_no || '').localeCompare(b.cons_no || '');
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [data.predictions, filter, sortBy, sortOrder, searchTerm]);

  // Statistiques
  const stats = data.summary;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          📊 Résultats de l'Analyse
        </h2>
        <p className="text-gray-600">
          Fichier : <span className="font-semibold">{data.filename}</span>
        </p>
      </div>

      {/* Statistiques Résumées */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-600 font-medium mb-1">Total Clients</p>
          <p className="text-3xl font-bold text-blue-900">{stats.total_clients}</p>
        </div>

        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-600 font-medium mb-1">Fraudeurs Détectés</p>
          <p className="text-3xl font-bold text-red-900">{stats.fraud_detected}</p>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-sm text-green-600 font-medium mb-1">Clients Normaux</p>
          <p className="text-3xl font-bold text-green-900">{stats.normal_count}</p>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-600 font-medium mb-1">Taux de Fraude</p>
          <p className="text-3xl font-bold text-yellow-900">
            {formatPercentage(stats.fraud_percentage / 100)}
          </p>
        </div>
      </div>

      {/* Filtres et Recherche */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        {/* Filtres */}
        <div className="flex space-x-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Tous ({data.predictions.length})
          </button>
          <button
            onClick={() => setFilter('fraud')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'fraud'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Fraudeurs ({stats.fraud_detected})
          </button>
          <button
            onClick={() => setFilter('normal')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'normal'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Normaux ({stats.normal_count})
          </button>
        </div>

        {/* Recherche */}
        <input
          type="text"
          placeholder="🔍 Rechercher un client (CONS_NO)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-full md:w-64"
        />
      </div>

      {/* Tri */}
      <div className="flex items-center space-x-4 mb-4 text-sm">
        <span className="text-gray-600 font-medium">Trier par :</span>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-3 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="probability">Score de Risque</option>
          <option value="cons_no">ID Client</option>
        </select>

        <button
          onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
          className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 transition-colors"
        >
          {sortOrder === 'asc' ? '⬆️ Croissant' : '⬇️ Décroissant'}
        </button>

        <span className="text-gray-500 ml-auto">
          {filteredData.length} résultat{filteredData.length > 1 ? 's' : ''}
        </span>
      </div>

      {/* Tableau */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b-2 border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                #
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                ID Client
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Score
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Prédiction
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                Niveau de Risque
              </th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                 Actions
               </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredData.map((item, index) => {
              const predLabel = formatPredictionLabel(item.prediction);

              return (
                <tr
                  key={item.index}
                  className="hover:bg-gray-50 transition-colors"
                >
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {index + 1}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {item.cons_no || `Client ${item.index}`}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span className="font-bold" style={{ color: predLabel.color }}>
                      {formatNumber(item.probability * 100, 1)}%
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span
                      className="px-3 py-1 rounded-full font-semibold text-xs"
                      style={{
                        backgroundColor: predLabel.bgColor,
                        color: predLabel.color,
                      }}
                    >
                      {predLabel.icon} {predLabel.text}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <RiskBadge riskLevel={item.risk_level} size="sm" />
                  </td>
                  <td className="px-4 py-3 text-sm">
                     <button
                       onClick={() => handleViewClient(item)}
                       className="text-blue-600 hover:text-blue-700 font-medium"
                          >
                           👁️ Voir
                        </button>
                    </td>
                  
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Message si aucun résultat */}
      {filteredData.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Aucun résultat trouvé
        </div>
      )}
    </div>
  );
};

export default BatchResults;