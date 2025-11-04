/**
 * Composant FileUploader - Zone de drag & drop pour CSV
 */
import React, { useState, useRef } from 'react';
import { CSV_CONFIG, MESSAGES } from '../../utils/constants';
import { formatFileSize } from '../../utils/formatters';

const FileUploader = ({ onUpload, isLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState(null);
  const [threshold, setThreshold] = useState(0.5);
  const fileInputRef = useRef(null);

  // Validation du fichier
  const validateFile = (file) => {
    // Vérifier l'extension
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    if (!CSV_CONFIG.acceptedExtensions.includes(extension)) {
      return `Seuls les fichiers CSV sont acceptés`;
    }

    // Vérifier la taille
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > CSV_CONFIG.maxSizeMB) {
      return `Le fichier est trop volumineux (max: ${CSV_CONFIG.maxSizeMB} MB)`;
    }

    return null;
  };

  // Gestion du drag & drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  // Gestion de la sélection de fichier
  const handleFileSelection = (file) => {
    const validationError = validateFile(file);
    
    if (validationError) {
      setError(validationError);
      setSelectedFile(null);
    } else {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  // Clic sur le bouton de sélection
  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  // Upload du fichier
  const handleUpload = () => {
    if (selectedFile && onUpload) {
      onUpload(selectedFile, threshold);
    }
  };

  // Reset
  const handleReset = () => {
    setSelectedFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Titre */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
           Upload Fichier CSV
        </h2>
        <p className="text-gray-600">
          Glissez-déposez votre fichier CSV ou cliquez pour sélectionner
        </p>
      </div>

      {/* Zone de drag & drop */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-50'
            : selectedFile
            ? 'border-green-500 bg-green-50'
            : error
            ? 'border-red-500 bg-red-50'
            : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        {/* Input caché */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileInput}
          className="hidden"
          disabled={isLoading}
        />

        {/* Icône */}
        <div className="mb-4">
          {selectedFile ? (
            <div className="text-6xl">✅</div>
          ) : (
            <div className="text-6xl">📄</div>
          )}
        </div>

        {/* Contenu selon l'état */}
        {selectedFile ? (
          // Fichier sélectionné
          <div>
            <p className="text-lg font-semibold text-green-700 mb-2">
              Fichier prêt !
            </p>
            <p className="text-gray-700 font-medium mb-1">
              {selectedFile.name}
            </p>
            <p className="text-sm text-gray-500">
              {formatFileSize(selectedFile.size)}
            </p>
          </div>
        ) : error ? (
          // Erreur
          <div>
            <p className="text-lg font-semibold text-red-700 mb-2">
              Fichier invalide
            </p>
            <p className="text-red-600">{error}</p>
          </div>
        ) : (
          // État initial
          <div>
            <p className="text-lg font-semibold text-gray-700 mb-2">
              Glissez-déposez un fichier CSV ici
            </p>
            <p className="text-gray-500 mb-4">ou</p>
            <button
              onClick={handleButtonClick}
              disabled={isLoading}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Sélectionner un fichier
            </button>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-4 text-sm text-gray-500">
          <p>Format accepté : CSV</p>
          <p>Taille max : {CSV_CONFIG.maxSizeMB} MB</p>
          <p>Colonnes requises : CONS_NO + au moins {CSV_CONFIG.minDays} jours de données</p>
        </div>
      </div>

      {/* Configuration du seuil */}
      {selectedFile && !error && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <label className="block text-sm font-semibold text-gray-700 mb-3">
            ⚙️ Seuil de Décision
          </label>
          
          <div className="flex items-center space-x-4">
            {/* Slider */}
            <input
              type="range"
              min="0.1"
              max="0.9"
              step="0.1"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              disabled={isLoading}
            />
            
            {/* Valeur */}
            <span className="text-lg font-bold text-blue-600 min-w-[60px]">
              {threshold.toFixed(1)}
            </span>
          </div>

          {/* Presets */}
          <div className="flex space-x-2 mt-3">
            <button
              onClick={() => setThreshold(0.3)}
              className={`px-3 py-1 text-sm rounded ${
                threshold === 0.3
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              disabled={isLoading}
            >
              Agressif (0.3)
            </button>
            <button
              onClick={() => setThreshold(0.5)}
              className={`px-3 py-1 text-sm rounded ${
                threshold === 0.5
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              disabled={isLoading}
            >
              Standard (0.5)
            </button>
            <button
              onClick={() => setThreshold(0.7)}
              className={`px-3 py-1 text-sm rounded ${
                threshold === 0.7
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              disabled={isLoading}
            >
              Conservateur (0.7)
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-2">
            Plus le seuil est bas, plus le modèle détecte de fraudeurs (mais plus de faux positifs)
          </p>
        </div>
      )}

      {/* Boutons d'action */}
      {selectedFile && !error && (
        <div className="mt-6 flex space-x-3">
          <button
            onClick={handleUpload}
            disabled={isLoading}
            className="flex-1 bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Analyse en cours...
              </>
            ) : (
              <>
                 Analyser
              </>
            )}
          </button>

          <button
            onClick={handleReset}
            disabled={isLoading}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            ↺ Réinitialiser
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUploader;