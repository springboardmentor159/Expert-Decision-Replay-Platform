import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createDecision } from "../../services/decisionService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Alert from "../../components/Alert";

const CreateDecision = () => {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [problemStatement, setProblemStatement] = useState("");
  const [category, setCategory] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!title.trim()) {
      setError("Title is required.");
      return;
    }

    if (!problemStatement.trim()) {
      setError("Problem statement is required.");
      return;
    }

    if (!category.trim()) {
      setError("Category is required.");
      return;
    }

    try {
      setLoading(true);

      const data = await createDecision({
        title: title.trim(),
        problem_statement: problemStatement.trim(),
        category: category.trim(),
      });

      navigate(`/decisions/${data.id}`);
    } catch (err) {
      console.error("Failed to create decision:", err);

      const status = err.response?.status;

      if (status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (status === 403) {
        setError("You are not authorized to create a decision.");
      } else if (status === 422) {
        setError("Please check all required fields.");
      } else if (status >= 500) {
        setError("Server error. Please try again later.");
      } else if (err.request) {
        setError(
          "Unable to connect to the backend. Please make sure FastAPI is running."
        );
      } else {
        setError("Failed to create decision.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-decision-page">

      <PageHeader
        title="Create Decision"
        subtitle="Create a new organizational decision"
      />

      {error && (
        <Alert
          message={error}
          type="error"
          onClose={() => setError("")}
        />
      )}

      <Card title="Decision Information">

        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="title">
              Decision Title *
            </label>

            <input
              id="title"
              type="text"
              value={title}
              onChange={(event) =>
                setTitle(event.target.value)
              }
              placeholder="Enter decision title"
              maxLength={200}
            />
          </div>

          <div className="form-group">
            <label htmlFor="problemStatement">
              Problem Statement *
            </label>

            <textarea
              id="problemStatement"
              value={problemStatement}
              onChange={(event) =>
                setProblemStatement(event.target.value)
              }
              placeholder="Describe the problem or situation requiring a decision"
              rows={6}
              maxLength={2000}
            />
          </div>

          <div className="form-group">
            <label htmlFor="category">
              Category *
            </label>

            <input
              id="category"
              type="text"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value)
              }
              placeholder="Example: Technology, Security, Finance"
              maxLength={100}
            />
          </div>

          <div className="create-decision-actions">

            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate("/decisions")}
              disabled={loading}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Creating..."
                : "Create Decision"}
            </Button>

          </div>

        </form>

      </Card>

    </div>
  );
};

export default CreateDecision;