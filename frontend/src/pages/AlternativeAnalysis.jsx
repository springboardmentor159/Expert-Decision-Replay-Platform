import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function AlternativeAnalysis() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [alternatives, setAlternatives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [editingAlternative, setEditingAlternative] =
    useState(null);

  const [comparison, setComparison] = useState(null);
  const [comparisonLoading, setComparisonLoading] =
    useState(false);
  const [comparisonError, setComparisonError] =
    useState("");

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    pros: "",
    cons: "",
    estimated_cost: "",
    feasibility_score: "",
    risk_level: "Low",
  });

  useEffect(() => {
    fetchAlternatives();
  }, [id]);

  const fetchAlternatives = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/decisions/${id}/alternatives`
      );

      setAlternatives(response.data);
    } catch (error) {
      console.error(
        "Failed to load alternatives:",
        error
      );

      if (error.response?.status === 404) {
        setError("Decision not found.");
      } else if (error.response?.status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (error.response?.status === 403) {
        setError(
          "You are not authorized to view these alternatives."
        );
      } else {
        setError("Unable to load alternatives.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      setError("Alternative name is required.");
      return false;
    }

    if (formData.feasibility_score === "") {
      setError("Feasibility score is required.");
      return false;
    }

    const feasibilityScore = Number(
      formData.feasibility_score
    );

    if (
      !Number.isInteger(feasibilityScore) ||
      feasibilityScore < 0 ||
      feasibilityScore > 5
    ) {
      setError(
        "Feasibility score must be an integer between 0 and 5."
      );
      return false;
    }

    if (
      formData.estimated_cost !== "" &&
      Number(formData.estimated_cost) < 0
    ) {
      setError("Estimated cost cannot be negative.");
      return false;
    }

    return true;
  };

  const resetForm = () => {
    setEditingAlternative(null);

    setFormData({
      name: "",
      description: "",
      pros: "",
      cons: "",
      estimated_cost: "",
      feasibility_score: "",
      risk_level: "Low",
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!validateForm()) {
      return;
    }

    try {
      const payload = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        pros: formData.pros.trim(),
        cons: formData.cons.trim(),
        estimated_cost:
          formData.estimated_cost === ""
            ? null
            : Number(formData.estimated_cost),
        feasibility_score: Number(
          formData.feasibility_score
        ),
        risk_level: formData.risk_level,
      };

      const response = await api.post(
        `/decisions/${id}/alternatives`,
        payload
      );

      setAlternatives((previous) => [
        ...previous,
        response.data,
      ]);

      resetForm();
      setComparison(null);
      setComparisonError("");

      setSuccess(
        "Alternative added successfully."
      );
    } catch (error) {
      console.error(
        "Failed to create alternative:",
        error
      );

      if (error.response?.status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (error.response?.status === 403) {
        setError(
          "You are not authorized to create an alternative."
        );
      } else if (error.response?.status === 404) {
        setError("Decision not found.");
      } else if (error.response?.status === 422) {
        setError(
          error.response?.data?.detail ||
            "Please check the alternative details."
        );
      } else {
        setError("Unable to create alternative.");
      }
    }
  };

  const handleEdit = (alternative) => {
    setEditingAlternative(alternative);

    setFormData({
      name: alternative.name || "",
      description: alternative.description || "",
      pros: alternative.pros || "",
      cons: alternative.cons || "",
      estimated_cost:
        alternative.estimated_cost ?? "",
      feasibility_score:
        alternative.feasibility_score ?? "",
      risk_level:
        alternative.risk_level || "Low",
    });

    setError("");
    setSuccess("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const handleUpdate = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!validateForm()) {
      return;
    }

    try {
      const payload = {
        name: formData.name.trim(),
        description: formData.description.trim(),
        pros: formData.pros.trim(),
        cons: formData.cons.trim(),
        estimated_cost:
          formData.estimated_cost === ""
            ? null
            : Number(formData.estimated_cost),
        feasibility_score: Number(
          formData.feasibility_score
        ),
        risk_level: formData.risk_level,
      };

      const response = await api.put(
        `/alternatives/${editingAlternative.id}`,
        payload
      );

      setAlternatives((previous) =>
        previous.map((item) =>
          item.id === editingAlternative.id
            ? response.data
            : item
        )
      );

      resetForm();
      setComparison(null);
      setComparisonError("");

      setSuccess(
        "Alternative updated successfully."
      );
    } catch (error) {
      console.error(
        "Failed to update alternative:",
        error
      );

      if (error.response?.status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (error.response?.status === 403) {
        setError(
          "You are not authorized to update this alternative."
        );
      } else if (error.response?.status === 404) {
        setError("Alternative not found.");
      } else if (error.response?.status === 422) {
        setError(
          error.response?.data?.detail ||
            "Please check the alternative details."
        );
      } else {
        setError("Unable to update alternative.");
      }
    }
  };
  const handleDelete = async (alternative) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${alternative.name}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      setSuccess("");

      await api.delete(
        `/alternatives/${alternative.id}`
      );

      setAlternatives((previous) =>
        previous.filter(
          (item) => item.id !== alternative.id
        )
      );

      setComparison(null);
      setComparisonError("");

      if (
        editingAlternative?.id === alternative.id
      ) {
        resetForm();
      }

      setSuccess(
        "Alternative deleted successfully."
      );
    } catch (error) {
      console.error(
        "Failed to delete alternative:",
        error
      );

      if (error.response?.status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (error.response?.status === 403) {
        setError(
          "You are not authorized to delete this alternative."
        );
      } else if (error.response?.status === 404) {
        setError("Alternative not found.");
      } else if (error.response?.status >= 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError(
          error.response?.data?.detail ||
            "Unable to delete alternative."
        );
      }
    }
  };

  const handleCompare = async () => {
    if (alternatives.length < 2) {
      setComparisonError(
        "Add at least two alternatives to compare them."
      );
      return;
    }

    try {
      setComparisonLoading(true);
      setComparisonError("");
      setComparison(null);

      const response = await api.get(
        `/decisions/${id}/alternatives/compare`
      );

      setComparison(response.data);
    } catch (error) {
      console.error(
        "Failed to compare alternatives:",
        error
      );

      if (error.response?.status === 401) {
        setComparisonError(
          "Your session has expired. Please login again."
        );
      } else if (error.response?.status === 403) {
        setComparisonError(
          "You are not authorized to compare alternatives."
        );
      } else if (error.response?.status === 404) {
        setComparisonError("Decision not found.");
      } else {
        setComparisonError(
          "Unable to compare alternatives."
        );
      }
    } finally {
      setComparisonLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <h1>Alternative Analysis</h1>
        <p>Loading alternatives...</p>
      </div>
    );
  }

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>Alternative Analysis</h1>
          <p>Decision #{id}</p>
        </div>

        <button
          type="button"
          onClick={() =>
            navigate(`/decisions/${id}`)
          }
        >
          ← Back
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}

      <div className="details-card">

        <h2>
          {editingAlternative
            ? "Edit Alternative"
            : "Add Alternative"}
        </h2>

        <form
          onSubmit={
            editingAlternative
              ? handleUpdate
              : handleSubmit
          }
        >

          <div className="form-group">
            <label>
              Alternative Name *
            </label>

            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter alternative name"
            />
          </div>

          <div className="form-group">
            <label>Description</label>

            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe this alternative"
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>Pros</label>

            <textarea
              name="pros"
              value={formData.pros}
              onChange={handleChange}
              placeholder="Advantages of this alternative"
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>Cons</label>

            <textarea
              name="cons"
              value={formData.cons}
              onChange={handleChange}
              placeholder="Disadvantages of this alternative"
              rows="3"
            />
          </div>

          <div className="details-grid">

            <div className="form-group">
              <label>Estimated Cost</label>

              <input
                type="number"
                name="estimated_cost"
                value={formData.estimated_cost}
                onChange={handleChange}
                placeholder="Enter cost"
                min="0"
              />
            </div>

            <div className="form-group">
              <label>
                Feasibility Score *
              </label>

              <input
                type="number"
                name="feasibility_score"
                value={formData.feasibility_score}
                onChange={handleChange}
                placeholder="0 - 5"
                min="0"
                max="5"
                step="1"
              />

              <small>
                Score must be between 0 and 5.
              </small>
            </div>

            <div className="form-group">
              <label>Risk Level</label>

              <select
                name="risk_level"
                value={formData.risk_level}
                onChange={handleChange}
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>

          </div>

          <button type="submit">
            {editingAlternative
              ? "Save Changes"
              : "Add Alternative"}
          </button>

          {editingAlternative && (
            <button
              type="button"
              onClick={() => {
                resetForm();
                setError("");
                setSuccess("");
              }}
            >
              Cancel
            </button>
          )}

        </form>
      </div>

      <div className="details-card">

        <h2>Existing Alternatives</h2>

        <button
          type="button"
          onClick={handleCompare}
          disabled={
            comparisonLoading ||
            alternatives.length < 2
          }
        >
          {comparisonLoading
            ? "Comparing..."
            : "Compare Alternatives"}
        </button>

        {alternatives.length < 2 && (
          <p>
            Add at least two alternatives to compare them.
          </p>
        )}

        {comparisonError && (
          <div className="error-message">
            {comparisonError}
          </div>
        )}

        {comparison && (
          <div className="details-card">

            <h2>Alternative Comparison</h2>

            {comparison.alternatives &&
            comparison.alternatives.length > 0 ? (
              <div className="decision-table-container">

                <table className="decision-table">

                  <thead>
                    <tr>
                      <th>Alternative</th>
                      <th>Estimated Cost</th>
                      <th>Feasibility Score</th>
                      <th>Risk Level</th>
                    </tr>
                  </thead>

                  <tbody>
                    {comparison.alternatives.map(
                      (alternative, index) => (
                        <tr key={index}>

                          <td className="decision-title">
                            {alternative.name || "N/A"}
                          </td>

                          <td>
                            {alternative.estimated_cost ??
                              "N/A"}
                          </td>

                          <td>
                            {alternative.feasibility_score ??
                              "N/A"}
                          </td>

                          <td>
                            {alternative.risk_level ||
                              "N/A"}
                          </td>

                        </tr>
                      )
                    )}
                  </tbody>

                </table>

              </div>
            ) : (
              <p>
                No alternatives available for comparison.
              </p>
            )}

          </div>
        )}

        {alternatives.length === 0 ? (
          <div className="empty-state">

            <h3>No alternatives found</h3>

            <p>
              No alternatives have been added to this
              decision yet.
            </p>

          </div>
        ) : (
          <div className="alternative-list">

            {alternatives.map((alternative) => (
              <div
                key={alternative.id}
                className="details-card"
              >

                <h2>
                  {alternative.name ||
                    "Unnamed Alternative"}
                </h2>

                <p>
                  {alternative.description ||
                    "No description provided."}
                </p>

                <div className="details-grid">

                  <div>
                    <strong>Pros</strong>

                    <p>
                      {alternative.pros || "N/A"}
                    </p>
                  </div>

                  <div>
                    <strong>Cons</strong>

                    <p>
                      {alternative.cons || "N/A"}
                    </p>
                  </div>

                  <div>
                    <strong>Estimated Cost</strong>

                    <p>
                      {alternative.estimated_cost ??
                        "N/A"}
                    </p>
                  </div>

                  <div>
                    <strong>Feasibility Score</strong>

                    <p>
                      {alternative.feasibility_score ??
                        "N/A"}
                    </p>
                  </div>

                  <div>
                    <strong>Risk Level</strong>

                    <p>
                      {alternative.risk_level || "N/A"}
                    </p>
                  </div>

                </div>

                <div className="decision-actions">

                  <button
                    type="button"
                    className="action-button edit-button"
                    onClick={() =>
                      handleEdit(alternative)
                    }
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    className="action-button delete-button"
                    onClick={() =>
                      handleDelete(alternative)
                    }
                  >
                    Delete
                  </button>

                </div>

              </div>
            ))}

          </div>
        )}

      </div>

    </div>
  );
}

export default AlternativeAnalysis;