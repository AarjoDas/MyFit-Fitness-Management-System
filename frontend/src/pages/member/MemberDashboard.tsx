import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { memberAPI } from '../../utils/api';
import { Link } from 'react-router-dom';

interface DashboardData {
  member: {
    member_id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  upcoming_sessions: Array<{
    session_id: number;
    scheduled_date: string;
    start_time: string;
    end_time: string;
    room_id: number;
    notes?: string;
  }>;
  upcoming_classes: Array<{
    enrollment_id: number;
    group_class: {
      class_id: number;
      class_name: string;
      scheduled_date: string;
      start_time: string;
    };
  }>;
}

const MemberDashboard: React.FC = () => {
  const { userId, logout } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (userId) {
      loadDashboard();
    }
  }, [userId]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const dashboardData = await memberAPI.getDashboard(userId!);
      setData(dashboardData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-600">{error || 'Failed to load dashboard'}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-indigo-600">Fitness Club</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {data.member.first_name}!</span>
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
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Member Dashboard</h2>
          <p className="text-gray-600">Member ID: {data.member.member_id} | Email: {data.member.email}</p>
        </div>

        <div className="mb-4">
          <button
            onClick={loadDashboard}
            className="text-indigo-600 hover:text-indigo-800 font-medium"
          >
            ↻ Refresh Dashboard
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link
            to="/member/book-pt"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Book Personal Training</h3>
            <p className="text-gray-600">Schedule a one-on-one session with a trainer</p>
          </Link>

          <Link
            to="/member/register-class"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Register for Group Class</h3>
            <p className="text-gray-600">Join a group fitness class</p>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Upcoming PT Sessions</h3>
            {data.upcoming_sessions.length === 0 ? (
              <p className="text-gray-500">No upcoming sessions</p>
            ) : (
              <div className="space-y-3">
                {data.upcoming_sessions.map((session) => (
                  <div key={session.session_id} className="border-l-4 border-indigo-500 pl-4 py-2">
                    <p className="font-medium text-gray-900">
                      {new Date(session.scheduled_date).toLocaleDateString()}
                    </p>
                    <p className="text-sm text-gray-600">
                      {session.start_time} - {session.end_time}
                    </p>
                    <p className="text-sm text-gray-600">Room ID: {session.room_id}</p>
                    {session.notes && (
                      <p className="text-sm text-gray-500 mt-1">Notes: {session.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Upcoming Classes</h3>
            {data.upcoming_classes.length === 0 ? (
              <p className="text-gray-500">No upcoming classes</p>
            ) : (
              <div className="space-y-3">
                {data.upcoming_classes
                  .filter((enrollment) => enrollment.group_class)
                  .map((enrollment) => (
                    <div key={enrollment.enrollment_id} className="border-l-4 border-green-500 pl-4 py-2">
                      <p className="font-medium text-gray-900">
                        {enrollment.group_class.class_name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(enrollment.group_class.scheduled_date).toLocaleDateString()}
                      </p>
                      <p className="text-sm text-gray-600">
                        {enrollment.group_class.start_time}
                      </p>
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemberDashboard;

