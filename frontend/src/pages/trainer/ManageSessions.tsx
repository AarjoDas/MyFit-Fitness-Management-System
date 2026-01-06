import React, { useState, useEffect } from 'react';
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
}

const ManageSessions: React.FC = () => {
  const { userId } = useAuth();
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [selectedSession, setSelectedSession] = useState<ScheduleItem | null>(null);
  const [newStatus, setNewStatus] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const today = new Date();
    const nextWeek = new Date(today);
    nextWeek.setDate(today.getDate() + 7);
    setStartDate(today.toISOString().split('T')[0]);
    setEndDate(nextWeek.toISOString().split('T')[0]);
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      loadSchedule();
    }
  }, [startDate, endDate, userId]);

  const loadSchedule = async () => {
    setLoading(true);
    setError('');

    try {
      const scheduleData = await trainerAPI.getSchedule(userId!, startDate, endDate);
      const ptSessions = scheduleData.filter((item: ScheduleItem) => item.type === 'PT Session');
      setSchedule(ptSessions);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSession || !newStatus) {
      setError('Please select a session and status');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await trainerAPI.updateSessionStatus(selectedSession.id, newStatus);
      if (notes) {
        await trainerAPI.updateSessionNotes(selectedSession.id, notes);
      }
      alert('Session updated successfully!');
      setSelectedSession(null);
      setNewStatus('');
      setNotes('');
      loadSchedule();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update session');
    } finally {
      setSubmitting(false);
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
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Manage PT Sessions</h2>

          <div className="mb-6 flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">PT Sessions</h3>
              {loading ? (
                <p className="text-gray-500">Loading...</p>
              ) : schedule.length === 0 ? (
                <p className="text-gray-500">No PT sessions found</p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {schedule.map((session) => (
                    <div
                      key={session.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedSession?.id === session.id
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => {
                        setSelectedSession(session);
                        setNewStatus(session.status || 'Scheduled');
                      }}
                    >
                      <p className="font-medium text-gray-900">{session.name}</p>
                      <p className="text-sm text-gray-600">
                        {new Date(session.date).toLocaleDateString()} | {session.start_time} - {session.end_time}
                      </p>
                      <p className="text-sm text-gray-600">Room: {session.room}</p>
                      <p className="text-sm text-gray-600">Status: {session.status || 'Scheduled'}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Update Session</h3>
              {selectedSession ? (
                <form onSubmit={handleUpdateStatus} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Session
                    </label>
                    <p className="text-sm text-gray-600 mb-2">{selectedSession.name}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Status
                    </label>
                    <select
                      value={newStatus}
                      onChange={(e) => setNewStatus(e.target.value)}
                      required
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    >
                      <option value="Scheduled">Scheduled</option>
                      <option value="Completed">Completed</option>
                      <option value="No Show">No Show</option>
                      <option value="Cancelled">Cancelled</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notes (Optional)
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {submitting ? 'Updating...' : 'Update Session'}
                  </button>
                </form>
              ) : (
                <p className="text-gray-500">Select a session to update</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManageSessions;

