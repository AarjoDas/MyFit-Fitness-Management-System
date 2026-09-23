import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI } from '../../utils/api';

const RecommendationMetrics: React.FC = () => {
  const [metrics, setMetrics] = useState<Record<string, any> | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await adminAPI.getRecommendationMetrics();
      setMetrics(data);
    } catch (err: any) {
      setMetrics(null);
      setError(err.response?.data?.detail || 'Failed to load metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  const handleRetrain = async () => {
    try {
      setRetraining(true);
      setError('');
      const data = await adminAPI.retrainRecommendations();
      setMetrics(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Retrain failed');
    } finally {
      setRetraining(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <Link to="/admin/dashboard" className="text-indigo-600 hover:text-indigo-800 font-medium">
            ← Back to Dashboard
          </Link>
          <h2 className="text-2xl font-bold text-gray-900 mt-4 mb-2">Recommendation Metrics</h2>
          <p className="text-gray-600 mb-6">
            Values come from the last run of <code>python -m ml.train</code> (synthetic historical data).
          </p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <button
            onClick={handleRetrain}
            disabled={retraining}
            className="mb-6 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {retraining ? 'Retraining...' : 'Retrain model'}
          </button>

          {loading ? (
            <p className="text-gray-500">Loading metrics...</p>
          ) : metrics ? (
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(metrics).map(([key, value]) => (
                <div key={key} className="border border-gray-200 rounded-lg p-4">
                  <dt className="text-sm text-gray-500">{key}</dt>
                  <dd className="text-lg font-medium text-gray-900">{String(value)}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <p className="text-gray-500">No metrics yet. Train the model first.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecommendationMetrics;
