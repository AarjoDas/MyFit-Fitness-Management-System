import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { commonAPI } from '../utils/api';

const Login: React.FC = () => {
  const [role, setRole] = useState<'member' | 'trainer' | 'admin'>('member');
  const [id, setId] = useState('');
  const [error, setError] = useState('');
  const [pendingNavigation, setPendingNavigation] = useState<string | null>(null);
  const { setUser, userRole } = useAuth();
  const navigate = useNavigate();

  // Navigate after state update completes
  useEffect(() => {
    if (userRole && pendingNavigation) {
      navigate(pendingNavigation);
      setPendingNavigation(null);
    }
  }, [userRole, pendingNavigation, navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const userId = parseInt(id);
    if (isNaN(userId) || userId <= 0) {
      setError('Please enter a valid ID');
      return;
    }

    try {
      // For simplicity, we'll just verify the ID exists
      // In a real app, you'd have proper authentication
      if (role === 'member') {
        const members = await commonAPI.getMembers();
        const member = members.find(m => m.member_id === userId);
        if (!member) {
          setError('Member ID not found');
          return;
        }
        setUser('member', userId);
        setPendingNavigation('/member/dashboard');
      } else if (role === 'trainer') {
        const trainers = await commonAPI.getTrainers();
        const trainer = trainers.find(t => t.trainer_id === userId);
        if (!trainer) {
          setError('Trainer ID not found');
          return;
        }
        setUser('trainer', userId);
        setPendingNavigation('/trainer/dashboard');
      } else if (role === 'admin') {
        // For admin, we'll just accept any ID for now
        // In production, you'd have proper admin authentication
        setUser('admin', userId);
        setPendingNavigation('/admin/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
          Fitness Club
        </h1>
        <p className="text-center text-gray-600 mb-8">Login to your account</p>

        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Role
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as any)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
              <option value="member">Member</option>
              <option value="trainer">Trainer</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {role === 'member' ? 'Member ID' : role === 'trainer' ? 'Trainer ID' : 'Admin ID'}
            </label>
            <input
              type="number"
              value={id}
              onChange={(e) => setId(e.target.value)}
              placeholder={`Enter your ${role} ID`}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150"
          >
            Login
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            New member?{' '}
            <Link to="/register" className="text-indigo-600 hover:text-indigo-800 font-medium">
              Register here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

