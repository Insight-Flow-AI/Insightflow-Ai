import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Auth from '../pages/Auth';
import Dashboard from '../pages/Dashboard';
import Upload from '../pages/Upload';
import Insights from '../pages/Dashboard/Insights';
import Chat from '../pages/Dashboard/Chat';
import Reports from '../pages/Reports';
import Settings from '../pages/Settings';
import { authService } from '../services/authService';

export default function AppRoutes() {
  const location = useLocation();
  const authenticated = authService.isAuthenticated();

  return (
    <Routes>
      <Route path="/login" element={<Auth />} />
      {authenticated ? (
        <>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </>
      ) : (
        <Route path="*" element={<Navigate to="/login" state={{ from: location }} replace />} />
      )}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
