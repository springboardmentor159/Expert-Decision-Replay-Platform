import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  createAlternative,
  getAlternative,
  updateAlternative,
} from "../../services/alternativeService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import Alert from "../../components/Alert";

const AlternativeForm = () => {
  const { decisionId, alternativeId } = useParams();
  const navigate = useNavigate();

  const isEditMode = Boolean(alternativeId);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [pros, setPros] = useState("");
  const [cons, setCons] = useState("");
  const [estimatedCost, setEstimatedCost] =
    useState("");
  const [feasibilityScore, setFeasibilityScore] =
    useState("");
  const [riskLevel, setRiskLevel] = useState("Low");

  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] =
    useState(isEditMode);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isEditMode) {
      return;
    }

    const loadAlternative = async () => {
      try {
        setLoadingData(true);
        setError("");

        const data = await getAlternative(
          alternativeId
        );

        setName(data.name || "");
        setDescription(data.description || "");
        setPros(data.pros || "");
        setCons(data.cons || "");

        setEstimatedCost(
          data.estimated_cost !== undefined &&
            data.estimated_cost !== null
            ? String(data.estimated_cost)
            : ""
        );

        setFeasibilityScore(
          data.feasibility_score !== undefined &&
            data.feasibility_score !== null
            ? String(data.feasibility_score)
            : ""
        );

        setRiskLevel(
          data.risk_level || "Low"
        );
      } catch (err) {
        console.error(
          "Failed to load alternative:",
          err
        );

        const status = err.response?.status;

        if (status === 401) {
          setError(
            "Your session has expired. Please login again."
          );
        } else if (status === 403) {
          setError(
            "You are not authorized to edit this alternative."
          );
        } else if (status === 404) {
          setError("Alternative not found.");
        } else if (status === 422) {
          setError("Invalid alternative ID.");
        } else if (status >= 500) {
          setError(
            "Server error. Please try again later."
          );
        } else {
          setError(
            "Failed to load alternative."
          );
        }
      } finally {
        setLoadingData(false);
      }
    };

    loadAlternative();
  }, [alternativeId, isEditMode]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!name.trim()) {
      setError("Alternative name is required.");
      return;
    }

    if (
      feasibilityScore === "" ||
      Number(feasibilityScore) < 1 ||
      Number(feasibilityScore) > 5
    ) {
      setError(
        "Feasibility score must be between 1 and 5."
      );
      return;
    }

    if (
      estimatedCost !== "" &&
      Number(estimatedCost) < 0
    ) {
      setError(
        "Estimated cost cannot be negative."
      );
      return;
    }

    try {
      setLoading(true);

      const alternativeData = {
        name: name.trim(),
        description: description.trim(),
        pros: pros.trim(),
        cons: cons.trim(),
        estimated_cost:
          estimatedCost.trim() === ""
            ? 0
            : Number(estimatedCost),
        feasibility_score:
          Number(feasibilityScore),
        risk_level: riskLevel,
      };

      if (isEditMode) {
        await updateAlternative(
          alternativeId,
          alternativeData
        );
      } else {
        await createAlternative(
          decisionId,
          alternativeData
        );
      }

      navigate(
        `/decisions/${decisionId}/alternatives`
      );
    } catch (err) {
      console.error(
        "Failed to save alternative:",
        err
      );

      const status = err.response?.status;

      if (status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (status === 403) {
        setError(
          "You are not authorized to modify alternatives."
        );
      } else if (status === 404) {
        setError(
          "Decision or alternative was not found."
        );
      } else if (status === 422) {
        setError(
          "Please check the alternative fields."
        );
      } else if (status >= 500) {
        setError(
          "Server error. Please try again later."
        );
      } else if (err.request) {
        setError(
          "Unable to connect to the backend. Please make sure FastAPI is running."
        );
      } else {
        setError(
          "Failed to save alternative."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  if (loadingData) {
    return (
      <div className="alternative-form-page">
        <PageHeader
          title="Edit Alternative"
          subtitle="Update decision alternative"
        />

        <Card>
          <div className="loading-state">
            Loading alternative...
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="alternative-form-page">
      <PageHeader
        title={
          isEditMode
            ? "Edit Alternative"
            : "Add Alternative"
        }
        subtitle={
          isEditMode
            ? "Update the selected decision alternative"
            : "Add a possible solution to this decision"
        }
      />

      {error && (
        <Alert
          message={error}
          type="error"
          onClose={() => setError("")}
        />
      )}

      <Card title="Alternative Information">
        <form onSubmit={handleSubmit}>

          <div className="form-group">
            <label htmlFor="alternativeName">
              Alternative Name *
            </label>

            <input
              id="alternativeName"
              type="text"
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              placeholder="Enter alternative name"
              maxLength={200}
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">
              Description
            </label>

            <textarea
              id="description"
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              placeholder="Describe this alternative"
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="pros">
              Pros
            </label>

            <textarea
              id="pros"
              value={pros}
              onChange={(event) =>
                setPros(event.target.value)
              }
              placeholder="List the advantages of this alternative"
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="cons">
              Cons
            </label>

            <textarea
              id="cons"
              value={cons}
              onChange={(event) =>
                setCons(event.target.value)
              }
              placeholder="List the disadvantages of this alternative"
              rows={4}
            />
          </div>

          <div className="alternative-form-grid">

            <div className="form-group">
              <label htmlFor="estimatedCost">
                Estimated Cost
              </label>

              <input
                id="estimatedCost"
                type="number"
                min="0"
                step="any"
                value={estimatedCost}
                onChange={(event) =>
                  setEstimatedCost(
                    event.target.value
                  )
                }
                placeholder="Enter estimated cost"
              />
            </div>

            <div className="form-group">
              <label htmlFor="feasibilityScore">
                Feasibility Score *
              </label>

              <input
                id="feasibilityScore"
                type="number"
                min="1"
                max="5"
                step="1"
                value={feasibilityScore}
                onChange={(event) =>
                  setFeasibilityScore(
                    event.target.value
                  )
                }
                placeholder="1 to 5"
              />
            </div>

          </div>

          <div className="form-group">
            <label htmlFor="riskLevel">
              Risk Level *
            </label>

            <select
              id="riskLevel"
              value={riskLevel}
              onChange={(event) =>
                setRiskLevel(
                  event.target.value
                )
              }
            >
              <option value="Low">Low</option>
              <option value="Medium">
                Medium
              </option>
              <option value="High">High</option>
            </select>
          </div>

          <div className="create-decision-actions">

            <Button
              type="button"
              variant="secondary"
              onClick={() =>
                navigate(
                  `/decisions/${decisionId}/alternatives`
                )
              }
              disabled={loading}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              disabled={loading}
            >
              {loading
                ? "Saving..."
                : isEditMode
                ? "Update Alternative"
                : "Create Alternative"}
            </Button>

          </div>

        </form>
      </Card>
    </div>
  );
};

export default AlternativeForm;