import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI } from '../../utils/api';
import { GroupClass, Trainer, Room } from '../../utils/api';

const ManageClasses: React.FC = () => {
  const [classes, setClasses] = useState<GroupClass[]>([]);
  const [trainers, setTrainers] = useState<Trainer[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showReschedule, setShowReschedule] = useState(false);
  const [selectedClass, setSelectedClass] = useState<GroupClass | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    trainer_id: '',
    room_id: '',
    scheduled_date: '',
    start_time: '',
    end_time: '',
    capacity: '',
  });
  const [rescheduleData, setRescheduleData] = useState({
    new_date: '',
    new_start: '',
    new_end: '',
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [classesData, trainersData, roomsData] = await Promise.all([
        adminAPI.getClasses(),
        adminAPI.getTrainers(),
        adminAPI.getRooms(),
      ]);
      setClasses(classesData);
      setTrainers(trainersData);
      setRooms(roomsData);
    } catch (err: any) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateClass = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await adminAPI.createClass({
        name: formData.name,
        trainer_id: parseInt(formData.trainer_id),
        room_id: parseInt(formData.room_id),
        scheduled_date: formData.scheduled_date,
        start_time: formData.start_time,
        end_time: formData.end_time,
        capacity: parseInt(formData.capacity),
      });
      alert('Class created successfully!');
      setFormData({
        name: '',
        trainer_id: '',
        room_id: '',
        scheduled_date: '',
        start_time: '',
        end_time: '',
        capacity: '',
      });
      setShowForm(false);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create class');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReschedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClass) return;

    setError('');
    setSubmitting(true);

    try {
      await adminAPI.rescheduleClass(
        selectedClass.class_id,
        rescheduleData.new_date,
        rescheduleData.new_start,
        rescheduleData.new_end
      );
      alert('Class rescheduled successfully!');
      setShowReschedule(false);
      setSelectedClass(null);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reschedule class');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = async (classId: number) => {
    if (!window.confirm('Are you sure you want to cancel this class?')) return;

    try {
      await adminAPI.cancelClass(classId);
      alert('Class cancelled successfully!');
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to cancel class');
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-4">
            <Link to="/admin/dashboard" className="text-indigo-600 hover:text-indigo-800 font-medium">
              ← Back to Dashboard
            </Link>
          </div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Manage Classes</h2>
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
            >
              {showForm ? 'Cancel' : 'Create Class'}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          {showForm && (
            <form onSubmit={handleCreateClass} className="mb-6 p-4 bg-gray-50 rounded-lg space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Class Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Trainer</label>
                  <select
                    value={formData.trainer_id}
                    onChange={(e) => setFormData({ ...formData, trainer_id: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Select trainer</option>
                    {trainers.map((t) => (
                      <option key={t.trainer_id} value={t.trainer_id}>
                        {t.first_name} {t.last_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Room</label>
                  <select
                    value={formData.room_id}
                    onChange={(e) => setFormData({ ...formData, room_id: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Select room</option>
                    {rooms.map((r) => (
                      <option key={r.room_id} value={r.room_id}>
                        {r.room_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                <input
                  type="date"
                  value={formData.scheduled_date}
                  onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                  <input
                    type="time"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
                  <input
                    type="time"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Capacity</label>
                  <input
                    type="number"
                    value={formData.capacity}
                    onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
                    required
                    min="1"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {submitting ? 'Creating...' : 'Create Class'}
              </button>
            </form>
          )}

          {showReschedule && selectedClass && (
            <form onSubmit={handleReschedule} className="mb-6 p-4 bg-yellow-50 rounded-lg space-y-4">
              <h3 className="font-semibold text-gray-900">Reschedule: {selectedClass.class_name}</h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">New Date</label>
                  <input
                    type="date"
                    value={rescheduleData.new_date}
                    onChange={(e) => setRescheduleData({ ...rescheduleData, new_date: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">New Start Time</label>
                  <input
                    type="time"
                    value={rescheduleData.new_start}
                    onChange={(e) => setRescheduleData({ ...rescheduleData, new_start: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">New End Time</label>
                  <input
                    type="time"
                    value={rescheduleData.new_end}
                    onChange={(e) => setRescheduleData({ ...rescheduleData, new_end: e.target.value })}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                  {submitting ? 'Rescheduling...' : 'Reschedule'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowReschedule(false);
                    setSelectedClass(null);
                  }}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          <div className="space-y-4">
            {classes.map((classItem) => (
              <div key={classItem.class_id} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-gray-900">{classItem.class_name}</h3>
                    <p className="text-sm text-gray-600">
                      {new Date(classItem.scheduled_date).toLocaleDateString()} | {classItem.start_time} - {classItem.end_time}
                    </p>
                    <p className="text-sm text-gray-600">
                      Capacity: {classItem.current_enrollment || 0} / {classItem.capacity}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setSelectedClass(classItem);
                        setRescheduleData({
                          new_date: classItem.scheduled_date,
                          new_start: classItem.start_time,
                          new_end: classItem.end_time,
                        });
                        setShowReschedule(true);
                      }}
                      className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600 text-sm"
                    >
                      Reschedule
                    </button>
                    <button
                      onClick={() => handleCancel(classItem.class_id)}
                      className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 text-sm"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManageClasses;

