import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import ProtectedRoute from './components/layout/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Organizations from './pages/Organizations'
import Projects from './pages/Projects'
import Uploads from './pages/Uploads'
import Billing from './pages/Billing'
import Anomalies from './pages/Anomalies'
import Forecast from './pages/Forecast'

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login"    element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard"                            element={<Dashboard />} />
        <Route path="organizations"                        element={<Organizations />} />
        <Route path="organizations/:orgId/projects"        element={<Projects />} />
        <Route path="organizations/:orgId/uploads"         element={<Uploads />} />
        <Route path="organizations/:orgId/billing"         element={<Billing />} />
        <Route path="anomalies"                            element={<Anomalies />} />
        <Route path="forecast"                             element={<Forecast />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
