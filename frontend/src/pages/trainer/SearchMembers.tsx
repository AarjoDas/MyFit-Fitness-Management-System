import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { trainerAPI, commonAPI } from '../../utils/api';
import { Member } from '../../utils/api';

const SearchMembers: React.FC = () => {
  const { userId } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [members, setMembers] = useState<Member[]>([]);
  const [selectedMember, setSelectedMember] = useState<Member | null>(null);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAllMembers();
  }, []);

  const loadAllMembers = async () => {
    try {
      const membersData = await commonAPI.getMembers();
      setMembers(membersData);
    } catch (err: any) {
      setError('Failed to load members');
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const results = await trainerAPI.searchMembers(userId!, searchQuery);
      setMembers(results);
      setSelectedMember(null);
      setProfile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleViewProfile = async (memberId: number) => {
    try {
      setLoading(true);
      const profileData = await trainerAPI.getMemberProfile(memberId);
      setProfile(profileData);
      const member = members.find(m => m.member_id === memberId);
      setSelectedMember(member || null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load profile');
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
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Search Members</h2>

          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex gap-4">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by name..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Members</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {members.map((member) => (
                  <div
                    key={member.member_id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedMember?.member_id === member.member_id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleViewProfile(member.member_id)}
                  >
                    <p className="font-medium text-gray-900">
                      {member.first_name} {member.last_name}
                    </p>
                    <p className="text-sm text-gray-600">ID: {member.member_id}</p>
                    <p className="text-sm text-gray-600">Email: {member.email}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Member Profile</h3>
              {profile ? (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">{profile.full_name}</h4>
                  <p className="text-sm text-gray-600 mb-1">Email: {profile.email}</p>
                  <p className="text-sm text-gray-600 mb-4">Gender: {profile.gender}</p>
                  <div>
                    <p className="font-medium text-gray-900 mb-2">Recent Activity:</p>
                    {profile.recent_activity && profile.recent_activity.length > 0 ? (
                      <ul className="list-disc list-inside space-y-1">
                        {profile.recent_activity.map((activity: string, index: number) => (
                          <li key={index} className="text-sm text-gray-600">{activity}</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-gray-500">No recent activity</p>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">Select a member to view profile</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchMembers;

