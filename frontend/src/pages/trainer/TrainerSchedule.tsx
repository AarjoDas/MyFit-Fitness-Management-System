import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { trainerAPI } from '../../utils/api';

interface ScheduleItem {
  type: string;
  id: number;
  name: string;
  date: string;
  start_time: string;
  end_time: string;
  room: string;
  status?: string;
  capacity_status?: string;
}

const TrainerSchedule: React.FC = () => {
  const { userId } = useAuth();
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLoadSchedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!startDate || !endDate) {
      setError('Please select both start and end dates');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const scheduleData = await trainerAPI.getSchedule(userId!, startDate, endDate);
      setSchedule(scheduleData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-4">
            <Link to="/trainer/dashboard" className="text-indigo-600 hover:text-indigo-800 font-medium">
              ← Back to Dashboard
            </Link>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">My Schedule</h2>

          <form onSubmit={handleLoadSchedule} className="mb-6 flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading}
                className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Load Schedule'}
              </button>
            </div>
          </form>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {schedule.length > 0 && (
            <div className="space-y-4">
              {schedule.map((item, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${
                    item.type === 'Group Class'
                      ? 'bg-blue-50 border-blue-500'
                      : 'bg-green-50 border-green-500'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-gray-900">{item.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {new Date(item.date).toLocaleDateString()} | {item.start_time} - {item.end_time}
                      </p>
                      <p className="text-sm text-gray-600">Room: {item.room}</p>
                      {item.status && (
                        <p className="text-sm text-gray-600">Status: {item.status}</p>
                      )}
                      {item.capacity_status && (
                        <p className="text-sm text-gray-600">Capacity: {item.capacity_status}</p>
                      )}
                    </div>
                    <span className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium">
                      {item.type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {schedule.length === 0 && !loading && startDate && endDate && (
            <p className="text-gray-500 text-center py-8">No sessions found for this date range</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainerSchedule;

