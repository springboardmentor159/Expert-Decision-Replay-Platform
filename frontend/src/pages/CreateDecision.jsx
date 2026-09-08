import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function CreateDecision() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    problem_statement: "",
    category: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMessage("");
    setError("");

    try {
      await api.post("/decisions", form);

      setMessage("Decision created successfully!");

      setTimeout(() => {
        navigate("/decisions");
      }, 1000);
    } catch (err) {
      console.error(err);

      if (err.response?.status === 401) {
        setError("Please login again.");
      } else if (err.response?.status === 403) {
        setError("You don't have permission to create a decision.");
      } else {
        setError("Failed to create decision.");
      }
    }
  };

  return (
    <div>
      <h1>Create Decision</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Title</label>
          <br />
          <input
            type="text"
            name="title"
            value={form.title}
            onChange={handleChange}
            placeholder="Enter decision title"
            required
          />
        </div>

        <br />

        <div>
          <label>Problem Statement</label>
          <br />
          <textarea
            name="problem_statement"
            value={form.problem_statement}
            onChange={handleChange}
            placeholder="Enter problem statement"
            rows="5"
            required
          />
        </div>

        <br />

        <div>
          <label>Category</label>
          <br />
          <input
            type="text"
            name="category"
            value={form.category}
            onChange={handleChange}
            placeholder="Enter category"
            required
          />
        </div>

        <br />

        <button type="submit">
          Create Decision
        </button>
      </form>

      <br />

      {message && <p>{message}</p>}
      {error && <p>{error}</p>}

      <button onClick={() => navigate("/decisions")}>
        Back to Decisions
      </button>
    </div>
  );
}

export default CreateDecision;