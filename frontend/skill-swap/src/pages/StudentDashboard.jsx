// src/pages/StudentDashboard.jsx
import React from 'react';
import { Link } from 'react-router-dom';

export default function StudentDashboard() {
  return (
    <div>
      <h2>Student Dashboard</h2>
      <nav>
        <ul>
          <li><Link to="/student/courses">Available Courses</Link></li>
          <li><Link to="/student/progress">Progress</Link></li>
          <li><Link to="/student/certificate">Certificates</Link></li>
          <li><Link to="/student/reviews">My Course Reviews</Link></li>
        </ul>
      </nav>
    </div>
  );
}
