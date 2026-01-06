import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const TrainerDashboard: React.FC = () => {
  const { userId, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-indigo-600">Fitness Club - Trainer Portal</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Trainer ID: {userId}</span>
              <button
                onClick={logout}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">Trainer Dashboard</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link
            to="/trainer/schedule"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-2">View Schedule</h3>
            <p className="text-gray-600">View your upcoming classes and PT sessions</p>
          </Link>

          <Link
            to="/trainer/members"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Search Members</h3>
            <p className="text-gray-600">Search and view member profiles</p>
          </Link>

          <Link
            to="/trainer/sessions"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Manage Sessions</h3>
            <p className="text-gray-600">Update session status and notes</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default TrainerDashboard;

