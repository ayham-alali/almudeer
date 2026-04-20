import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { initializeSyncManager } from './services/syncManager';

// Auth Pages
import SplashScreen from './pages/auth/SplashScreen';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import VerifyEmail from './pages/auth/VerifyEmail';
import PendingApproval from './pages/auth/PendingApproval';

// Main Layout & Views
import MainLayout from './components/layout/MainLayout';
import TasksPage from './pages/tasks/TasksPage';
import TaskForm from './pages/tasks/TaskForm';
import NotesPage from './pages/notes/NotesPage';
import NoteForm from './pages/notes/NoteForm';
import CustomersPage from './pages/customers/CustomersPage';
import CustomerForm from './pages/customers/CustomerForm';
import CustomerDetails from './pages/customers/CustomerDetails';
import ProfilePage from './pages/profile/ProfilePage';
import UserProfile from './pages/profile/UserProfile';
import NotificationsPage from './pages/notifications/NotificationsPage';

export default function App() {
  
  useEffect(() => {
    initializeSyncManager();
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 font-sans text-gray-900 dark:text-gray-100 transition-colors selection:bg-blue-500/30">
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/" element={<SplashScreen />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/pending-approval" element={<PendingApproval />} />

          {/* Fully Screen Views Overlays */}
          <Route path="/tasks/new" element={<TaskForm />} />
          <Route path="/tasks/:id" element={<TaskForm />} />
          <Route path="/notes/new" element={<NoteForm />} />
          <Route path="/notes/:id" element={<NoteForm />} />
          <Route path="/customers/new" element={<CustomerForm />} />
          <Route path="/customers/:id" element={<CustomerDetails />} />
          <Route path="/users/:id" element={<UserProfile />} />
          <Route path="/notifications" element={<NotificationsPage />} />

          {/* Authenticated Context inside App Shell Layout */}
          <Route element={<MainLayout />}>
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/notes" element={<NotesPage />} /> 
            <Route path="/customers" element={<CustomersPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
