import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from "./context/AuthContext";
import Register from './pages/register';
import Navbar from './components/Navbar';
import Login from './pages/login';
import register from './pages/register';
import AdminRoutes from './Routes/AdminRoutes';
import TeacherRoutes from './Routes/TeacherRoutes';
import StudentRoutes from './Routes/StudentRoutes';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navbar />

        <Routes>
          {/* Auth Pages */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Role-Based Dashboards */}
          <Route path="/admin/*" element={<AdminRoutes />} />
          <Route path="/teacher/*" element={<TeacherRoutes />} />
          <Route path="/student/*" element={<StudentRoutes />} />

          {/* Default route */}
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
