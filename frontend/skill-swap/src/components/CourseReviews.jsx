import React, { useEffect, useState } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext.jsx";

const API = "http://127.0.0.1:5000"; // Backend base URL

function CourseReviews({ courseId }) {
  const { user } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");

  // Fetch reviews when course loads
  useEffect(() => {
    axios.get(`${API}/courses/${courseId}/reviews`)
      .then(res => setReviews(res.data))
      .catch(err => console.error("Error fetching reviews:", err));
  }, [courseId]);

  // Submit a new review
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!rating) return alert("Please provide a rating");

    try {
      await axios.post(
        `${API}/courses/${courseId}/reviews`,
        { rating, comment },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );
      alert("Review submitted!");
      setRating(0);
      setComment("");
      const res = await axios.get(`${API}/courses/${courseId}/reviews`);
      setReviews(res.data);
    } catch (err) {
      console.error("Error submitting review:", err);
      alert("Failed to post review");
    }
  };

  return (
    <div>
      <h3>Course Reviews</h3>

      {/* Add Review Form (only for students) */}
      {user?.role === "student" && (
        <form onSubmit={handleSubmit}>
          <div>
            <label>Rating (1–5): </label>
            <input
              type="number"
              min="1"
              max="5"
              value={rating}
              onChange={(e) => setRating(Number(e.target.value))}
            />
          </div>
          <div>
            <label>Comment: </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows="3"
              cols="40"
            />
          </div>
          <button type="submit">Submit Review</button>
        </form>
      )}

      {/* Display Reviews */}
      <ul>
        {reviews.length > 0 ? (
          reviews.map((rev) => (
            <li key={rev.id}>
              <strong>{rev.user_name}</strong> rated <b>{rev.rating}</b>/5
              <p>{rev.comment}</p>
            </li>
          ))
        ) : (
          <p>No reviews yet.</p>
        )}
      </ul>
    </div>
  );
}

export default CourseReviews;
