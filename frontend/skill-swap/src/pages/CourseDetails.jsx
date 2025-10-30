import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

const API = "http://127.0.0.1:5000/api"; // adjust if backend URL changes

export default function CourseDetails() {
  const { id } = useParams(); // Get course ID from URL
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isPaying, setIsPaying] = useState(false);
  const token = localStorage.getItem("token");

  // Fetch the course by ID
  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const res = await axios.get(`${API}/student/course/${id}`);
        setCourse(res.data);
      } catch (err) {
        console.error("Error fetching course:", err);
        setError("Could not load course details.");
      } finally {
        setLoading(false);
      }
    };

    fetchCourse();
  }, [id]);

  // Handle payment
  const handlePayment = async () => {
    if (!course) return;
    setIsPaying(true);

    try {
      const res = await axios.post(
        `${API}/payment/process`,
        { course_id: course.id, amount: course.price },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      console.log("Payment success:", res.data);
      alert("Payment successful! You now have access to the course.");
    } catch (err) {
      console.error("Payment error:", err.response?.data || err.message);
      alert(" Payment failed. Please try again later.");
    } finally {
      setIsPaying(false);
    }
  };

  if (loading) return <p>Loading course details...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!course) return <p>Course not found.</p>;

  return (
    <div className="container mt-4">
      <div className="card shadow p-4">
        <h2>{course.title}</h2>
        <p>{course.description}</p>
        <p>
          <strong>Teacher:</strong> {course.teacher_name || "Unknown"}
        </p>
        <p>
          <strong>Price:</strong> KES {course.price}
        </p>

        <button
          className="btn btn-success"
          onClick={handlePayment}
          disabled={isPaying}
        >
          {isPaying ? "Processing Payment..." : "Pay & Start Course"}
        </button>
      </div>
    </div>
  );
}
