import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';

// Member pages
import MemberDashboard from './pages/member/MemberDashboard';
import BookPT from './pages/member/BookPT';
import RegisterClass from './pages/member/RegisterClass';

// Trainer pages
import TrainerDashboard from './pages/trainer/TrainerDashboard';
import TrainerSchedule from './pages/trainer/TrainerSchedule';
import SearchMembers from './pages/trainer/SearchMembers';
import ManageSessions from './pages/trainer/ManageSessions';

// Admin pages
import AdminDashboard from './pages/admin/AdminDashboard';
import ManageRooms from './pages/admin/ManageRooms';
import ManageTrainers from './pages/admin/ManageTrainers';
import ManageClasses from './pages/admin/ManageClasses';
import ViewMembers from './pages/admin/ViewMembers';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Member routes */}
          <Route
            path="/member/dashboard"
            element={
              <ProtectedRoute requiredRole="member">
                <MemberDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/member/book-pt"
            element={
              <ProtectedRoute requiredRole="member">
                <BookPT />
              </ProtectedRoute>
            }
          />
          <Route
            path="/member/register-class"
            element={
              <ProtectedRoute requiredRole="member">
                <RegisterClass />
              </ProtectedRoute>
            }
          />

          {/* Trainer routes */}
          <Route
            path="/trainer/dashboard"
            element={
              <ProtectedRoute requiredRole="trainer">
                <TrainerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trainer/schedule"
            element={
              <ProtectedRoute requiredRole="trainer">
                <TrainerSchedule />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trainer/members"
            element={
              <ProtectedRoute requiredRole="trainer">
                <SearchMembers />
              </ProtectedRoute>
            }
          />
          <Route
            path="/trainer/sessions"
            element={
              <ProtectedRoute requiredRole="trainer">
                <ManageSessions />
              </ProtectedRoute>
            }
          />

          {/* Admin routes */}
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute requiredRole="admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/rooms"
            element={
              <ProtectedRoute requiredRole="admin">
                <ManageRooms />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/trainers"
            element={
              <ProtectedRoute requiredRole="admin">
                <ManageTrainers />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/classes"
            element={
              <ProtectedRoute requiredRole="admin">
                <ManageClasses />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/members"
            element={
              <ProtectedRoute requiredRole="admin">
                <ViewMembers />
              </ProtectedRoute>
            }
          />

          {/* Default route */}
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
