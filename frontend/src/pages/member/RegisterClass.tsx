import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { memberAPI, commonAPI } from '../../utils/api';
import { GroupClass } from '../../utils/api';

const RegisterClass: React.FC = () => {
  const { userId } = useAuth();
  const navigate = useNavigate();
  const [classes, setClasses] = useState<GroupClass[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [selectedClass, setSelectedClass] = useState('');

  useEffect(() => {
    loadClasses();
  }, []);

  const loadClasses = async () => {
    try {
      const classesData = await commonAPI.getClasses();
      setClasses(classesData);
    } catch (err: any) {
      setError('Failed to load classes');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedClass) {
      setError('Please select a class');
      return;
    }

    setError('');
    setSubmitting(true);

    try {
      await memberAPI.enrollInClass(userId!, parseInt(selectedClass));
      alert('Successfully enrolled in class!');
      navigate('/member/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to enroll in class');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-50 flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-4">
            <Link to="/member/dashboard" className="text-indigo-600 hover:text-indigo-800 font-medium">
              ← Back to Dashboard
            </Link>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Register for Group Class</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Available Classes
              </label>
              {classes.length === 0 ? (
                <p className="text-gray-500">No classes available</p>
              ) : (
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {classes.map((classItem) => (
                    <label
                      key={classItem.class_id}
                      className={`block p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                        selectedClass === classItem.class_id.toString()
                          ? 'border-indigo-500 bg-indigo-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="class"
                        value={classItem.class_id}
                        checked={selectedClass === classItem.class_id.toString()}
                        onChange={(e) => setSelectedClass(e.target.value)}
                        className="mr-3"
                      />
                      <div className="inline-block">
                        <span className="font-semibold text-gray-900">{classItem.class_name}</span>
                        <div className="text-sm text-gray-600 mt-1">
                          <p>Date: {new Date(classItem.scheduled_date).toLocaleDateString()}</p>
                          <p>Time: {classItem.start_time} - {classItem.end_time}</p>
                          <p>
                            Enrollment: {classItem.current_enrollment || 0} / {classItem.capacity}
                            {classItem.is_full && <span className="text-red-600 ml-2">(Full)</span>}
                          </p>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              )}
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={submitting || !selectedClass}
                className="flex-1 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {submitting ? 'Enrolling...' : 'Enroll in Class'}
              </button>
              <button
                type="button"
                onClick={() => navigate('/member/dashboard')}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterClass;

