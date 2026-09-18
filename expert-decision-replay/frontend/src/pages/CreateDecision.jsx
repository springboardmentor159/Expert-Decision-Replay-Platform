import { useState } from "react";
import "./CreateDecision.css";
import api from "../api";

function CreateDecision() {
  const [title, setTitle] = useState("");
  const [problemStatement, setProblemStatement] = useState("");
  const [category, setCategory] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage("");
    setLoading(true);

    try {
      const response = await api.post("/decisions", {
        title: title,
        problem_statement: problemStatement,
        category: category,
      });

      console.log("Created decision:", response.data);

      setMessage("Decision created successfully!");

      setTitle("");
      setProblemStatement("");
      setCategory("");
    } catch (error) {
      console.error("Error creating decision:", error);

      const detail = error.response?.data?.detail;

      if (Array.isArray(detail)) {
        setMessage(
          detail
            .map((item) => `${item.loc?.join(".")}: ${item.msg}`)
            .join(" | ")
        );
      } else if (typeof detail === "string") {
        setMessage(detail);
      } else {
        setMessage("Failed to create decision.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-decision-page">
      <div className="create-decision-card">
        <h1>Create Decision</h1>

        <p>Enter the decision details below.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="title">Decision Title</label>

          <input
            id="title"
            type="text"
            placeholder="Enter decision title"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            required
          />

          <label htmlFor="problemStatement">
            Problem Statement
          </label>

          <textarea
            id="problemStatement"
            placeholder="Enter problem statement"
            value={problemStatement}
            onChange={(event) =>
              setProblemStatement(event.target.value)
            }
            rows="5"
            required
          ></textarea>

          <label htmlFor="category">Category</label>

          <input
            id="category"
            type="text"
            placeholder="Enter category"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            required
          />

          <button type="submit" disabled={loading}>
            {loading ? "Submitting..." : "Submit Decision"}
          </button>
        </form>

        {message && <p className="success-message">{message}</p>}
      </div>
    </div>
  );
}

export default CreateDecision;